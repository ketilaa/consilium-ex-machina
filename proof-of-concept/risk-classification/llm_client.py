"""Minimal client for OpenAI-compatible chat endpoints -- local (llama.cpp
server) or hosted (Groq), model-tiering test only.

Local endpoints are the verbatim, already-validated transport used across
every PoC in this series. GROQ_MODEL is new, for the model-tiering test:
does a genuinely stronger model (120B vs. our local ~24B quantized model)
fix the classification failures found in rounds 2-3, or do they persist
regardless of model, pointing at a mechanism problem instead? The API key
is read from the environment by name at call time, never passed as a
literal string or logged/printed anywhere in this codebase.
"""

import os

import requests

OWNER_MODEL = {
    "base_url": "http://localhost:8081",
    "model": "bartowski/mistralai_Mistral-Small-3.1-24B-Instruct-2503-GGUF",
}
SUPPORT_MODEL = OWNER_MODEL

GROQ_MODEL = {
    "base_url": "https://api.groq.com/openai",
    "model": "openai/gpt-oss-120b",
    "api_key_env": "GROQ_API_KEY",
}


def chat(endpoint, system, user, temperature=0.3, max_tokens=600, timeout=180):
    headers = {}
    api_key_env = endpoint.get("api_key_env")
    if api_key_env:
        api_key = os.environ.get(api_key_env)
        if not api_key:
            raise RuntimeError(f"Environment variable {api_key_env} is not set")
        headers["Authorization"] = f"Bearer {api_key}"

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
        headers=headers,
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
