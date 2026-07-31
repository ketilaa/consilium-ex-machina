"""Minimal client for local OpenAI-compatible chat endpoints (llama.cpp server)."""

import requests

REASONING_MODEL = {"base_url": "http://localhost:8080", "model": "Qwen/Qwen2.5-Coder-14B-Instruct-GGUF"}
SMALL_MODEL = {"base_url": "http://localhost:8081", "model": "Qwen/Qwen2.5-7B-Instruct-GGUF"}


def chat(endpoint, system, user, temperature=0.3, max_tokens=700, timeout=480):
    response = requests.post(
        f"{endpoint['base_url']}/v1/chat/completions",
        json={
            "model": endpoint["model"],
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
        timeout=timeout,
    )
    result = response.json()
    if response.status_code != 200 or "choices" not in result:
        return {"ok": False, "status_code": response.status_code, "raw": result}
    return {
        "ok": True,
        "content": result["choices"][0]["message"]["content"].strip(),
        "usage": result.get("usage", {}),
    }
