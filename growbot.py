#!/usr/bin/env python3
"""GrowBot Privado — asistente CLI para cultivo outdoor de CBD Auto en Torremolinos.

Uso:
    export ANTHROPIC_API_KEY=sk-ant-...
    python3 growbot.py
"""

from __future__ import annotations

import json
import os
import sys
from datetime import date
from pathlib import Path

from anthropic import Anthropic, APIError

MODEL = "claude-opus-4-7"
STATE_FILE = Path.home() / ".growbot.json"
HISTORY_CAP = 40

STAGES = [
    ("germen", "Germinación"),
    ("seedling", "Plántula"),
    ("veg", "Vegetativo"),
    ("preflor", "Prefloración"),
    ("flora", "Floración"),
    ("cosecha", "Cosecha"),
]

SYSTEM = (
    "Eres GrowBot Privado, asistente experto en cultivo outdoor de cannabis CBD Auto "
    "en Torremolinos, Málaga (España), costa mediterránea. Clima suave, mucho sol, "
    "veranos cálidos y secos, inviernos templados. El usuario cultiva legalmente para "
    "uso personal. Responde en español, claro y directo, con consejos prácticos y "
    "seguros. Evita juicios morales. Si te preguntan por dosis de nutrientes, sé "
    "conservador y explica señales de exceso. Incluye unidades métricas. Si falta "
    "info clave (día, etapa, síntoma concreto), pide una aclaración breve antes de "
    "recomendar."
)

QUICK = [
    "Revisar riego de hoy",
    "¿Signos de deficiencia?",
    "Plan de nutrientes semanal",
    "¿Cuándo cosechar?",
    "Problemas de plagas frecuentes",
]

ANSI = {
    "reset": "\033[0m",
    "dim": "\033[2m",
    "bold": "\033[1m",
    "green": "\033[32m",
    "cyan": "\033[36m",
    "yellow": "\033[33m",
    "red": "\033[31m",
    "grey": "\033[90m",
}


def color(text: str, *styles: str) -> str:
    return "".join(ANSI[s] for s in styles) + text + ANSI["reset"]


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {"day": 1, "stage": "veg", "history": []}


def save_state(state: dict) -> None:
    state["history"] = state["history"][-HISTORY_CAP:]
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2))


def print_banner(state: dict) -> None:
    stage_label = dict(STAGES).get(state["stage"], state["stage"])
    print(color("GrowBot Privado", "bold", "green"))
    print(color(f"Torremolinos, Málaga  ·  {date.today().isoformat()}", "dim"))
    print(color(f"Día {state['day']}  ·  Etapa: {stage_label}", "cyan"))
    print(color("Comandos: /day N  /stage X  /clear  /quick  /help  /quit", "dim"))
    print()


def print_help() -> None:
    print(color("Comandos disponibles:", "bold"))
    print("  /day N       Fija el día del cultivo (entero)")
    print("  /stage X     Cambia la etapa. Opciones:")
    for key, label in STAGES:
        print(f"               - {key:10s} {label}")
    print("  /clear       Borra el historial")
    print("  /quick       Muestra preguntas rápidas")
    print("  /help        Muestra esta ayuda")
    print("  /quit        Salir (también Ctrl+D)")
    print()


def print_quick() -> None:
    print(color("Preguntas rápidas:", "bold"))
    for i, q in enumerate(QUICK, 1):
        print(f"  {i}. {q}")
    print(color("Escribe el número o redacta tu pregunta.", "dim"))
    print()


def handle_command(cmd: str, state: dict) -> bool:
    """Returns True if the command was handled, False if it should be treated as a message."""
    parts = cmd.strip().split(maxsplit=1)
    name = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""

    if name in ("/quit", "/exit"):
        save_state(state)
        print(color("Hasta luego.", "dim"))
        sys.exit(0)
    if name == "/help":
        print_help()
        return True
    if name == "/quick":
        print_quick()
        return True
    if name == "/clear":
        state["history"] = []
        save_state(state)
        print(color("Historial borrado.", "yellow"))
        return True
    if name == "/day":
        try:
            state["day"] = max(1, int(arg))
            save_state(state)
            print(color(f"Día fijado a {state['day']}.", "cyan"))
        except ValueError:
            print(color("Uso: /day <entero>", "red"))
        return True
    if name == "/stage":
        valid = {k for k, _ in STAGES}
        if arg in valid:
            state["stage"] = arg
            save_state(state)
            print(color(f"Etapa: {dict(STAGES)[arg]}", "cyan"))
        else:
            print(color(f"Etapas válidas: {', '.join(valid)}", "red"))
        return True
    return False


def stream_reply(client: Anthropic, state: dict, user_text: str) -> None:
    prefix = f"[Día {state['day']}, etapa: {state['stage']}]\n"
    user_turn = {"role": "user", "content": prefix + user_text}
    messages = state["history"] + [user_turn]

    print(color("GrowBot  ", "bold", "green"), end="", flush=True)
    chunks: list[str] = []
    try:
        with client.messages.stream(
            model=MODEL,
            max_tokens=1024,
            system=[{"type": "text", "text": SYSTEM, "cache_control": {"type": "ephemeral"}}],
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                chunks.append(text)
                print(text, end="", flush=True)
        print()
    except KeyboardInterrupt:
        print(color("  [interrumpido]", "yellow"))
    except APIError as e:
        print(color(f"\n[Error de API] {e}", "red"))
        return

    answer = "".join(chunks).strip()
    if answer:
        state["history"].append(user_turn)
        state["history"].append({"role": "assistant", "content": answer})
        save_state(state)


def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        try:
            api_key = input("Pega tu ANTHROPIC_API_KEY: ").strip()
        except EOFError:
            print(color("Falta ANTHROPIC_API_KEY.", "red"))
            sys.exit(1)
    if not api_key:
        print(color("Falta ANTHROPIC_API_KEY.", "red"))
        sys.exit(1)

    client = Anthropic(api_key=api_key)
    state = load_state()
    print_banner(state)

    while True:
        try:
            raw = input(color("Tú> ", "bold", "cyan"))
        except (EOFError, KeyboardInterrupt):
            print()
            save_state(state)
            print(color("Hasta luego.", "dim"))
            return

        text = raw.strip()
        if not text:
            continue
        if text.startswith("/"):
            handle_command(text, state)
            continue
        if text.isdigit() and 1 <= int(text) <= len(QUICK):
            text = QUICK[int(text) - 1]
            print(color(f"   -> {text}", "dim"))

        stream_reply(client, state, text)
        print()


if __name__ == "__main__":
    main()
