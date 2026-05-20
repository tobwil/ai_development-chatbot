#!/usr/bin/env python3
"""Minimal teaching backend for a multi-provider AI chatbot frontend."""

from __future__ import annotations

import json
import os
import ssl
import urllib.error
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "static"
PORT = int(os.environ.get("PORT", "5173"))

try:
    import certifi

    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CONTEXT = ssl.create_default_context()


class ChatbotHandler(SimpleHTTPRequestHandler):
    """Serves the frontend and proxies chat requests to selected AI providers."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def end_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

    def do_GET(self) -> None:
        if self.path == "/":
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self) -> None:
        if self.path != "/api/chat":
            self.send_json({"error": "Unknown endpoint"}, status=404)
            return

        try:
            payload = self.read_json()
            result = call_provider(payload)
            self.send_json(result)
        except ValueError as exc:
            self.send_json({"error": str(exc)}, status=400)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            self.send_json(
                {
                    "error": f"Provider returned HTTP {exc.code}",
                    "details": safe_json_or_text(body),
                },
                status=502,
            )
        except urllib.error.URLError as exc:
            self.send_json({"error": f"Network error: {exc.reason}"}, status=502)
        except Exception as exc:  # noqa: BLE001 - useful in a small teaching server.
            self.send_json({"error": f"Server error: {exc}"}, status=500)

    def read_json(self) -> dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length <= 0:
            raise ValueError("Request body is empty.")
        raw = self.rfile.read(content_length)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError("Request body must be valid JSON.") from exc
        if not isinstance(data, dict):
            raise ValueError("Request body must be a JSON object.")
        return data

    def send_json(self, data: dict[str, Any], status: int = 200) -> None:
        encoded = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def call_provider(payload: dict[str, Any]) -> dict[str, Any]:
    provider = require_string(payload, "provider").lower()
    api_key = require_string(payload, "apiKey")
    model = require_string(payload, "model")
    system_prompt = str(payload.get("systemPrompt", "")).strip()
    messages = payload.get("messages")

    if not isinstance(messages, list) or not messages:
        raise ValueError("messages must be a non-empty list.")

    normalized_messages = normalize_messages(messages)

    if provider == "openai":
        return call_openai(api_key, model, system_prompt, normalized_messages)
    if provider == "anthropic":
        return call_anthropic(api_key, model, system_prompt, normalized_messages)
    if provider == "gemini":
        return call_gemini(api_key, model, system_prompt, normalized_messages)

    raise ValueError("provider must be one of: openai, anthropic, gemini.")


def require_string(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} is required.")
    return value.strip()


def normalize_messages(messages: list[Any]) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for message in messages:
        if not isinstance(message, dict):
            raise ValueError("Every message must be an object.")
        role = message.get("role")
        content = message.get("content")
        if role not in {"user", "assistant"}:
            raise ValueError("Message roles must be user or assistant.")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Every message needs text content.")
        normalized.append({"role": role, "content": content.strip()})
    return normalized


def post_json(url: str, headers: dict[str, str], body: dict[str, Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60, context=SSL_CONTEXT) as response:
        return json.loads(response.read().decode("utf-8"))


def call_openai(
    api_key: str, model: str, system_prompt: str, messages: list[dict[str, str]]
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "model": model,
        "input": [
            {
                "role": message["role"],
                "content": [{"type": "input_text", "text": message["content"]}],
            }
            for message in messages
        ],
    }
    if system_prompt:
        body["instructions"] = system_prompt

    data = post_json(
        "https://api.openai.com/v1/responses",
        {"Authorization": f"Bearer {api_key}"},
        body,
    )
    return {"reply": extract_openai_text(data), "raw": data}


def call_anthropic(
    api_key: str, model: str, system_prompt: str, messages: list[dict[str, str]]
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "model": model,
        "max_tokens": 1024,
        "messages": messages,
    }
    if system_prompt:
        body["system"] = system_prompt

    data = post_json(
        "https://api.anthropic.com/v1/messages",
        {"x-api-key": api_key, "anthropic-version": "2023-06-01"},
        body,
    )
    return {"reply": extract_anthropic_text(data), "raw": data}


def call_gemini(
    api_key: str, model: str, system_prompt: str, messages: list[dict[str, str]]
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "contents": [
            {
                "role": "user" if message["role"] == "user" else "model",
                "parts": [{"text": message["content"]}],
            }
            for message in messages
        ]
    }
    if system_prompt:
        body["systemInstruction"] = {"parts": [{"text": system_prompt}]}

    data = post_json(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        {"x-goog-api-key": api_key},
        body,
    )
    return {"reply": extract_gemini_text(data), "raw": data}


def extract_openai_text(data: dict[str, Any]) -> str:
    output_text = data.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    parts: list[str] = []
    for item in data.get("output", []):
        if not isinstance(item, dict):
            continue
        for content in item.get("content", []):
            if isinstance(content, dict) and isinstance(content.get("text"), str):
                parts.append(content["text"])
    return "\n".join(parts).strip() or "No text output returned."


def extract_anthropic_text(data: dict[str, Any]) -> str:
    parts = [
        item["text"]
        for item in data.get("content", [])
        if isinstance(item, dict) and item.get("type") == "text" and isinstance(item.get("text"), str)
    ]
    return "\n".join(parts).strip() or "No text output returned."


def extract_gemini_text(data: dict[str, Any]) -> str:
    parts: list[str] = []
    for candidate in data.get("candidates", []):
        content = candidate.get("content", {}) if isinstance(candidate, dict) else {}
        for part in content.get("parts", []):
            if isinstance(part, dict) and isinstance(part.get("text"), str):
                parts.append(part["text"])
    return "\n".join(parts).strip() or "No text output returned."


def safe_json_or_text(raw: str) -> Any:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw[:2000]


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", PORT), ChatbotHandler)
    print(f"Teaching chatbot running at http://127.0.0.1:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
