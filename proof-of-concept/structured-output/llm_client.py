"""Minimal client for local OpenAI-compatible chat endpoints (llama.cpp server).

Adds optional `response_format` support over the other PoCs' client: llama.cpp's
server compiles a JSON-schema response_format into a grammar and performs
genuinely constrained decoding (verified empirically against this repo's local
server before building this PoC), not just a prompted hint.
"""

import requests

MODEL = {
    "base_url": "http://localhost:8081",
    "model": "bartowski/mistralai_Mistral-Small-3.1-24B-Instruct-2503-GGUF",
}


def chat(endpoint, system, user, temperature=0.3, max_tokens=500, timeout=180, response_format=None):
    payload = {
        "model": endpoint["model"],
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if response_format is not None:
        payload["response_format"] = response_format
    response = requests.post(f"{endpoint['base_url']}/v1/chat/completions", json=payload, timeout=timeout)
    result = response.json()
    if response.status_code != 200 or "choices" not in result:
        return {"ok": False, "status_code": response.status_code, "raw": result}
    choice = result["choices"][0]
    return {
        "ok": True,
        "content": choice["message"]["content"].strip(),
        "finish_reason": choice.get("finish_reason"),
        "usage": result.get("usage", {}),
    }
