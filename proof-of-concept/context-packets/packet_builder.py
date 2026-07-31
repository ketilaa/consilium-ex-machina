"""Explicit rule-based Context Packet construction — no embeddings, no LLM calls.

Selection is: keyword overlap between the task text and each file's own
"signature" (filename words + docstring + top-level def/class names), plus one
hop of local import dependencies from whatever matched, plus a fixed file
(conventions.md) that's always included. This is deliberately the cheap,
explainable alternative to embeddings/RAG that docs/high-level-architecture.md
floats as an option for Context Packet construction.
"""

import ast
import re
from pathlib import Path

STOPWORDS = {
    "the", "a", "an", "and", "or", "to", "of", "for", "in", "on", "is", "are",
    "what", "why", "how", "must", "you", "your", "it", "if", "this", "that",
    "with", "from", "by", "be", "do", "not", "before", "new", "add", "each",
    "every", "existing", "already", "into", "could", "would", "go", "wrong",
    "skip", "skipped", "should", "let", "lets", "them",
}

ALWAYS_INCLUDE = ["conventions.md"]


def _words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) > 2 and w not in STOPWORDS}


def _split_identifier(name: str) -> set[str]:
    # snake_case and CamelCase -> individual lowercase words
    name = re.sub(r"(?<!^)(?=[A-Z])", "_", name)
    return _words(name.replace("_", " "))


def _load_corpus(repo_dir: Path) -> dict[str, str]:
    return {f.name: f.read_text() for f in sorted(repo_dir.iterdir()) if f.is_file()}


def _file_signature(filename: str, content: str) -> set[str]:
    keywords = _split_identifier(Path(filename).stem)
    if filename.endswith(".py"):
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return keywords
        docstring = ast.get_docstring(tree) or ""
        keywords |= _words(docstring)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                keywords |= _split_identifier(node.name)
    else:
        keywords |= _words(content[:1000])
    return keywords


def _local_imports(filename: str, content: str, corpus_stems: set[str]) -> set[str]:
    if not filename.endswith(".py"):
        return set()
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return set()
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {alias.name for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    return {f"{name}.py" for name in imported if name in corpus_stems}


def build_packet(task_question: str, repo_dir: Path, top_k: int = 6) -> tuple[list[str], str]:
    corpus = _load_corpus(repo_dir)
    corpus_stems = {Path(name).stem for name in corpus}
    task_keywords = _words(task_question)

    scores = {}
    for filename, content in corpus.items():
        signature = _file_signature(filename, content)
        overlap = len(task_keywords & signature)
        if overlap > 0:
            scores[filename] = overlap

    selected = sorted(scores, key=scores.get, reverse=True)[:top_k]

    for filename in list(selected):
        selected += [
            f for f in _local_imports(filename, corpus[filename], corpus_stems)
            if f not in selected
        ]

    for filename in ALWAYS_INCLUDE:
        if filename in corpus and filename not in selected:
            selected.append(filename)

    ordered = [f for f in ALWAYS_INCLUDE if f in selected]
    ordered += [f for f in selected if f not in ordered]

    packet_text = "\n\n".join(f"### {name}\n\n{corpus[name]}" for name in ordered)
    return ordered, packet_text


def full_dump(repo_dir: Path) -> str:
    corpus = _load_corpus(repo_dir)
    return "\n\n".join(f"### {name}\n\n{content}" for name, content in corpus.items())
