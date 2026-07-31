"""Minimal client for local OpenAI-compatible chat endpoints (llama.cpp server)."""

import requests

OWNER_MODEL = {"base_url": "http://localhost:8080", "model": "Qwen/Qwen2.5-Coder-14B-Instruct-GGUF"}
SUPPORT_MODEL = {"base_url": "http://localhost:8081", "model": "Qwen/Qwen2.5-7B-Instruct-GGUF"}


def chat(endpoint, system, user, temperature=0.4, max_tokens=700, timeout=180):
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
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()
