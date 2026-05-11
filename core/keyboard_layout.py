"""
Spanish keyboard layout (with Ç) for the virtual keyboard widget.
Each key has:
  - normal / shifted / altgr labels  (what appears on the keycap)
  - typertask_token (if the key maps to a Typertask special; else None → literal char)
  - hold_pair (if True, two sub-buttons are rendered: Down / Up)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Tuple


@dataclass
class Key:
    normal: str                        # label bottom-left of keycap
    shifted: str = ""                  # label top-left  (Shift held)
    altgr: str = ""                    # label bottom-right (AltGr held)
    width: float = 1.0                 # relative width units
    typertask_token: Optional[str] = None   # e.g. "{enter}"
    hold_pair: bool = False            # generates ShiftDown/ShiftUp twins

    @property
    def display(self) -> str:
        """Primary label shown on key."""
        return self.normal


# ── Row definitions ───────────────────────────────────────────────────────────
# Each row is a list of Keys.
# Special keys that Typertask supports carry typertask_token.
# Keys with hold_pair=True are modifiers that will be split into Down/Up buttons.

ROWS: List[List[Key]] = [
    # ── Row 0: Esc + F-keys ──────────────────────────────────────────────────
    [
        Key("Esc",  typertask_token="{escape}", width=1.0),
        Key("", width=0.5),  # gap
        Key("F1",  typertask_token="{F1}"),
        Key("F2",  typertask_token="{F2}"),
        Key("F3",  typertask_token="{F3}"),
        Key("F4",  typertask_token="{F4}"),
        Key("", width=0.3),
        Key("F5",  typertask_token="{F5}"),
        Key("F6",  typertask_token="{F6}"),
        Key("F7",  typertask_token="{F7}"),
        Key("F8",  typertask_token="{F8}"),
        Key("", width=0.3),
        Key("F9",  typertask_token="{F9}"),
        Key("F10", typertask_token="{F10}"),
        Key("F11", typertask_token="{F11}"),
        Key("F12", typertask_token="{F12}"),
    ],

    # ── Row 1: numbers ───────────────────────────────────────────────────────
    [
        Key("º", "ª", "\\"),
        Key("1", "!", "|"),
        Key("2", '"', "@"),
        Key("3", "·", "#"),
        Key("4", "$", "~"),
        Key("5", "%", "€"),
        Key("6", "&"),
        Key("7", "/"),
        Key("8", "("),
        Key("9", ")"),
        Key("0", "="),
        Key("'", "?"),
        Key("¡", "¿"),
        Key("⌫", width=2.0, typertask_token="{backspace}"),
    ],

    # ── Row 2: QWERTY ────────────────────────────────────────────────────────
    [
        Key("Tab", width=1.5, typertask_token="{tab}"),
        Key("q", "Q"),
        Key("w", "W"),
        Key("e", "E", "€"),
        Key("r", "R"),
        Key("t", "T"),
        Key("y", "Y"),
        Key("u", "U"),
        Key("i", "I"),
        Key("o", "O"),
        Key("p", "P"),
        Key("`", "^"),
        Key("+", "*", "~"),
        Key("↵", width=1.5, typertask_token="{enter}"),
    ],

    # ── Row 3: ASDF ──────────────────────────────────────────────────────────
    [
        Key("⇪", width=1.8),   # Caps Lock — no typertask token
        Key("a", "A"),
        Key("s", "S"),
        Key("d", "D"),
        Key("f", "F"),
        Key("g", "G"),
        Key("h", "H"),
        Key("j", "J"),
        Key("k", "K"),
        Key("l", "L"),
        Key("ñ", "Ñ"),
        Key("´", "¨"),
        Key("ç", "Ç"),
    ],

    # ── Row 4: ZXCV ──────────────────────────────────────────────────────────
    [
        Key("Shift", width=2.2,
            typertask_token="{Shift}",
            hold_pair=True),
        Key("z", "Z"),
        Key("x", "X"),
        Key("c", "C"),
        Key("v", "V"),
        Key("b", "B"),
        Key("n", "N"),
        Key("m", "M"),
        Key(",", ";"),
        Key(".", ":"),
        Key("-", "_"),
        Key("Shift", width=2.8,
            typertask_token="{Shift}",
            hold_pair=True),
    ],

    # ── Row 5: bottom ────────────────────────────────────────────────────────
    [
        Key("Ctrl", width=1.4,
            typertask_token="{Control}",
            hold_pair=True),
        Key("Win",  width=1.2, typertask_token="{Win}"),
        Key("Alt",  width=1.2,
            typertask_token="{Alt}",
            hold_pair=True),
        Key(" ", width=6.5, typertask_token=None),    # Space bar — literal space
        Key("AltGr", width=1.2,
            typertask_token="{Alt}",
            hold_pair=True),
        Key("Win",   width=1.0, typertask_token="{Win}"),
        Key("Menu",  width=1.0),
        Key("Ctrl",  width=1.4,
            typertask_token="{Control}",
            hold_pair=True),
    ],
]

# ── Navigation cluster ────────────────────────────────────────────────────────
NAV_CLUSTER: List[List[Key]] = [
    [
        Key("Ins",  typertask_token="{insert}"),
        Key("Home", typertask_token="{home}"),
        Key("PgUp", typertask_token="{pageup}"),
    ],
    [
        Key("Del",  typertask_token="{delete}"),
        Key("End",  typertask_token="{end}"),
        Key("PgDn", typertask_token="{pagedown}"),
    ],
    [],   # blank row for spacing
    [
        Key(""),
        Key("↑",    typertask_token="{up}"),
        Key(""),
    ],
    [
        Key("←",    typertask_token="{left}"),
        Key("↓",    typertask_token="{down}"),
        Key("→",    typertask_token="{right}"),
    ],
]

# ── Numpad cluster ────────────────────────────────────────────────────────────
# NumLock / / * - on top row, then 7-8-9 + (tall), 4-5-6, 1-2-3 Enter (tall), 0 (wide) .
NUMPAD_ROWS: List[List[Key]] = [
    [
        Key("NumLk"),
        Key("/"),
        Key("*"),
        Key("-"),
    ],
    [
        Key("7\nNum7", typertask_token="{Num7}"),
        Key("8\nNum8", typertask_token="{Num8}"),
        Key("9\nNum9", typertask_token="{Num9}"),
        Key("+",  width=1.0),   # tall + — rendered as normal for simplicity
    ],
    [
        Key("4\nNum4", typertask_token="{Num4}"),
        Key("5\nNum5", typertask_token="{Num5}"),
        Key("6\nNum6", typertask_token="{Num6}"),
        Key("",   width=1.0),   # placeholder for + continuation
    ],
    [
        Key("1\nNum1", typertask_token="{Num1}"),
        Key("2\nNum2", typertask_token="{Num2}"),
        Key("3\nNum3", typertask_token="{Num3}"),
        Key("↵",  width=1.0, typertask_token="{enter}"),  # tall enter
    ],
    [
        Key("0\nNum0", typertask_token="{Num0}", width=2.0),
        Key("",   width=1.0),   # placeholder for 0 continuation
        Key(".",  width=1.0),
        Key("",   width=1.0),   # placeholder for enter continuation
    ],
]
