"""
Typertask shortcut definitions and autocomplete logic.
Pure data/logic — no UI dependencies.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Shortcut:
    token: str          # what gets inserted, e.g. "{Control}"
    label: str          # display label on button
    category: str       # grouping
    description: str = ""
    on_keyboard: bool = False  # True → already shown on the virtual keyboard


# ── Shortcut catalogue ────────────────────────────────────────────────────────
# on_keyboard=True  → key exists on the virtual keyboard; palette hides these.
# on_keyboard=False → palette-only shortcut.

SHORTCUTS: List[Shortcut] = [
    # ── Modifiers (pulse) ────────────────────────────────────────────────────
    Shortcut("{Control}", "Ctrl",   "modifier", "Pulsa Control",        on_keyboard=True),
    Shortcut("{ctrl}",    "{ctrl}", "modifier", "Alias de Control",     on_keyboard=False),
    Shortcut("{Alt}",     "Alt",    "modifier", "Pulsa Alt",            on_keyboard=True),
    Shortcut("{Shift}",   "Shift",  "modifier", "Pulsa Shift",          on_keyboard=True),
    Shortcut("{Win}",     "Win",    "modifier", "Pulsa tecla Windows",  on_keyboard=True),
    Shortcut("{escape}",  "Esc",    "modifier", "Escape",               on_keyboard=True),

    # ── Hold / release pairs ─────────────────────────────────────────────────
    Shortcut("{controldown}", "CtrlDown",  "hold", "Mantener Control presionado", on_keyboard=True),
    Shortcut("{controlup}",   "CtrlUp",   "hold", "Soltar Control",              on_keyboard=True),
    Shortcut("{shiftdown}",   "ShiftDown","hold", "Mantener Shift presionado",   on_keyboard=True),
    Shortcut("{shiftup}",     "ShiftUp",  "hold", "Soltar Shift",                on_keyboard=True),
    Shortcut("{altdown}",     "AltDown",  "hold", "Mantener Alt presionado",     on_keyboard=True),
    Shortcut("{altup}",       "AltUp",    "hold", "Soltar Alt",                  on_keyboard=True),

    # ── Navigation ───────────────────────────────────────────────────────────
    Shortcut("{left}",     "←",    "navigation", "Flecha izquierda",  on_keyboard=True),
    Shortcut("{right}",    "→",    "navigation", "Flecha derecha",    on_keyboard=True),
    Shortcut("{up}",       "↑",    "navigation", "Flecha arriba",     on_keyboard=True),
    Shortcut("{down}",     "↓",    "navigation", "Flecha abajo",      on_keyboard=True),
    Shortcut("{home}",     "Home", "navigation", "Inicio de línea",   on_keyboard=True),
    Shortcut("{end}",      "End",  "navigation", "Fin de línea",      on_keyboard=True),
    Shortcut("{pageup}",   "PgUp", "navigation", "Página arriba",     on_keyboard=True),
    Shortcut("{pagedown}", "PgDn", "navigation", "Página abajo",      on_keyboard=True),

    # ── Editing ──────────────────────────────────────────────────────────────
    Shortcut("{tab}",       "Tab",    "editing", "Tabulador",  on_keyboard=True),
    Shortcut("{enter}",     "Enter",  "editing", "Intro",      on_keyboard=True),
    Shortcut("{return}",    "Return", "editing", "Return (alias de Enter)", on_keyboard=False),
    Shortcut("{backspace}", "⌫",      "editing", "Retroceso",  on_keyboard=True),
    Shortcut("{delete}",    "Del",    "editing", "Suprimir",   on_keyboard=True),
    Shortcut("{insert}",    "Ins",    "editing", "Insertar",   on_keyboard=True),

    # ── Delays ───────────────────────────────────────────────────────────────
    Shortcut("{delay=500}",  "⏱ 500ms", "timing", "Pausa 500 ms",    on_keyboard=False),
    Shortcut("{delay=1000}", "⏱ 1s",    "timing", "Pausa 1 segundo", on_keyboard=False),
    Shortcut("{delay=2000}", "⏱ 2s",    "timing", "Pausa 2 segundos",on_keyboard=False),

    # ── Run command ──────────────────────────────────────────────────────────
    Shortcut("=RUN: ", "RUN:", "command", "Ejecutar programa/script", on_keyboard=False),

    # ── Date / Time tokens ───────────────────────────────────────────────────
    Shortcut("{{yyyy}}", "{{yyyy}}", "datetime", "Año 4 dígitos",  on_keyboard=False),
    Shortcut("{{yy}}",   "{{yy}}",  "datetime", "Año 2 dígitos",  on_keyboard=False),
    Shortcut("{{mm}}",   "{{mm}}",  "datetime", "Mes",            on_keyboard=False),
    Shortcut("{{dd}}",   "{{dd}}",  "datetime", "Día del mes",    on_keyboard=False),
    Shortcut("{{hh}}",   "{{hh}}",  "datetime", "Hora",           on_keyboard=False),
    Shortcut("{{uu}}",   "{{uu}}",  "datetime", "Minutos",        on_keyboard=False),

    # ── Volume ───────────────────────────────────────────────────────────────
    Shortcut("{VolumeMute}",  "🔇 Mute", "media", "Silenciar volumen", on_keyboard=False),
    Shortcut("{VolumeUp}",    "🔊 Vol+", "media", "Subir volumen",     on_keyboard=False),
    Shortcut("{VolumeDown}",  "🔉 Vol-", "media", "Bajar volumen",     on_keyboard=False),

    # ── Numpad ───────────────────────────────────────────────────────────────
    *[Shortcut(f"{{Num{n}}}", f"Num{n}", "numpad",
               f"Teclado numérico {n}", on_keyboard=True) for n in range(10)],

    # ── Function keys ────────────────────────────────────────────────────────
    *[Shortcut(f"{{F{n}}}", f"F{n}", "function",
               f"Tecla función F{n}", on_keyboard=True) for n in range(1, 13)],
]


# ── Autocomplete engine ───────────────────────────────────────────────────────

def get_suggestions(query: str, max_results: int = 10) -> List[Shortcut]:
    """
    Return shortcuts whose token or description contain *query* (case-insensitive).
    Prioritises prefix matches over substring matches.
    """
    if not query:
        return []
    q = query.lower()
    prefix, substring = [], []
    for s in SHORTCUTS:
        haystack = (s.token + s.label + s.description).lower()
        token_low = s.token.lower()
        if token_low.startswith(q) or s.label.lower().startswith(q):
            prefix.append(s)
        elif q in haystack:
            substring.append(s)
    return (prefix + substring)[:max_results]


def all_tokens() -> List[str]:
    return [s.token for s in SHORTCUTS]


def category_order() -> List[str]:
    seen, order = set(), []
    for s in SHORTCUTS:
        if s.category not in seen:
            order.append(s.category)
            seen.add(s.category)
    return order
