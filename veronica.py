#!/usr/bin/env python3
"""Veronica: local terminal assistant backed by Ollama."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_MODEL = "qwen3:8b"
DEFAULT_URL = "http://127.0.0.1:11434"
SYSTEM = (
    "Você é Veronica, uma assistente de IA local criada por Neo, um desenvolvedor solo. "
    "Quando perguntarem quem é seu dono ou criador, responda: Neo, um dev solo. "
    "Responda de forma direta, útil e honesta. Use o idioma do usuário. "
    "Não afirme ter executado ações que não executou."
)
BANNER = r"""
██╗   ██╗███████╗██████╗  ██████╗ ███╗   ██╗██╗ ██████╗ █████╗
██║   ██║██╔════╝██╔══██╗██╔═══██╗████╗  ██║██║██╔════╝██╔══██╗
██║   ██║█████╗  ██████╔╝██║   ██║██╔██╗ ██║██║██║     ███████║
╚██╗ ██╔╝██╔══╝  ██╔══██╗██║   ██║██║╚██╗██║██║██║     ██╔══██║
 ╚████╔╝ ███████╗██║  ██║╚██████╔╝██║ ╚████║██║╚██████╗██║  ██║
  ╚═══╝  ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝ ╚═════╝╚═╝  ╚═╝
""".strip("\n")
RESET = "\033[0m"
DIM = "\033[2m"
BOLD = "\033[1m"
VIOLET = "\033[38;2;176;135;255m"
PINK = "\033[38;2;255;123;189m"
CYAN = "\033[38;2;110;220;238m"
GRAY = "\033[38;2;159;161;181m"


def paint(text: str, color: str, enabled: bool) -> str:
    return f"{color}{text}{RESET}" if enabled else text


def api(base: str, path: str, payload: dict | None = None, timeout: int = 30):
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(
        base.rstrip("/") + path,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST" if data is not None else "GET",
    )
    return urllib.request.urlopen(request, timeout=timeout)


def available_models(base: str) -> list[str]:
    with api(base, "/api/tags") as response:
        return [entry["name"] for entry in json.load(response).get("models", [])]


def chat(base: str, model: str, messages: list[dict], on_chunk):
    payload = {"model": model, "messages": messages, "stream": True}
    chunks = []
    with api(base, "/api/chat", payload, timeout=600) as response:
        for line in response:
            if not line.strip():
                continue
            event = json.loads(line)
            if event.get("error"):
                raise RuntimeError(event["error"])
            chunk = event.get("message", {}).get("content", "")
            if chunk:
                chunks.append(chunk)
                on_chunk(chunk)
    return "".join(chunks)


def print_header(model: str, color: bool):
    width = shutil.get_terminal_size((80, 20)).columns
    if width >= 75:
        shades = [VIOLET, VIOLET, PINK, PINK, CYAN, CYAN]
        for line, shade in zip(BANNER.splitlines(), shades):
            print(paint(line, shade, color))
    else:
        print(paint("✦ V E R O N I C A", VIOLET + BOLD, color))
    print(paint("  ✦  inteligência local  /  criada por Neo", GRAY, color))
    print(paint(f"  ◈  {model}  •  /ajuda para comandos\n", CYAN, color))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Veronica — sua IA local no terminal")
    parser.add_argument("prompt", nargs="*", help="Pergunta única; sem argumento abre o chat")
    parser.add_argument("--model", default=os.getenv("VERONICA_MODEL", DEFAULT_MODEL))
    parser.add_argument("--url", default=os.getenv("OLLAMA_HOST", DEFAULT_URL))
    parser.add_argument("--no-color", action="store_true")
    args = parser.parse_args(argv)
    color = sys.stdout.isatty() and not args.no_color and "NO_COLOR" not in os.environ
    base = args.url.rstrip("/")
    print_header(args.model, color)
    try:
        models = available_models(base)
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        print(paint("Ollama indisponível.", PINK, color))
        print(f"Inicie o serviço: ollama serve\nDetalhe: {exc}", file=sys.stderr)
        return 1
    if args.model not in models and args.model + ":latest" not in models:
        print(paint(f"Modelo {args.model!r} não instalado.", PINK, color))
        print(f"Instale com: ollama pull {args.model}")
        if models:
            print("Disponíveis: " + ", ".join(models))
        return 1
    messages = [{"role": "system", "content": SYSTEM}]
    single = bool(args.prompt)
    print(paint("  pronto para conversar", DIM, color))
    while True:
        try:
            prompt = " ".join(args.prompt) if single else input(paint("\n❯ ", VIOLET + BOLD, color))
        except (EOFError, KeyboardInterrupt):
            print("\nAté logo.")
            return 0
        prompt = prompt.strip()
        if not prompt:
            if single:
                return 0
            continue
        if prompt in ("/sair", "/exit", "/quit"):
            print("Até logo.")
            return 0
        if prompt == "/ajuda":
            print("/ajuda   comandos\n/limpar  limpa a conversa\n/modelo  mostra o modelo\n/sair    encerra")
            if single:
                return 0
            continue
        if prompt == "/limpar":
            messages = messages[:1]
            print("Conversa limpa.")
            if single:
                return 0
            continue
        if prompt == "/modelo":
            print(args.model)
            if single:
                return 0
            continue
        messages.append({"role": "user", "content": prompt})
        print(paint("\n✦ Veronica  ", PINK + BOLD, color), end="", flush=True)
        try:
            answer = chat(base, args.model, messages, lambda part: print(part, end="", flush=True))
            print()
            messages.append({"role": "assistant", "content": answer})
        except (urllib.error.URLError, TimeoutError, OSError, ValueError, RuntimeError) as exc:
            messages.pop()
            print(f"\nErro ao consultar o modelo: {exc}", file=sys.stderr)
            if single:
                return 1
        if single:
            return 0


if __name__ == "__main__":
    raise SystemExit(main())
