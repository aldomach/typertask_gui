"""
VirtualKeyboard widget — renders the Spanish keyboard layout.
Emits key_pressed(str) signal with the token/char to insert.
"""
from __future__ import annotations
from typing import Callable

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QSizePolicy, QFrame, QLabel,
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont

from core.keyboard_layout import ROWS, NAV_CLUSTER, NUMPAD_ROWS, Key


# ── Hold-state tracker ────────────────────────────────────────────────────────

class _HoldState:
    """Tracks Down/Up toggle for modifier keys."""
    def __init__(self):
        self._active: dict[str, bool] = {}  # token -> is_down

    def toggle(self, token: str) -> str:
        """Returns the token to emit ({xdown} or {xup}) and updates state."""
        base = token.strip("{}").lower()     # e.g. "shift"
        down_tok = "{" + base + "down}"
        up_tok   = "{" + base + "up}"
        is_down = self._active.get(base, False)
        if not is_down:
            self._active[base] = True
            return down_tok
        else:
            self._active[base] = False
            return up_tok

    def is_down(self, token: str) -> bool:
        base = token.strip("{}").lower()
        return self._active.get(base, False)


# ── Key button ────────────────────────────────────────────────────────────────

class KeyButton(QPushButton):
    UNIT = 32   # pixels per width-unit

    def __init__(self, key: Key, hold_state: _HoldState,
                 emit: Callable[[str], None], parent=None):
        super().__init__(parent)
        self._key = key
        self._hold_state = hold_state
        self._emit = emit

        w = max(int(key.width * self.UNIT), 8)
        self.setFixedWidth(w)
        self.setFixedHeight(self.UNIT - 2)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self._refresh_label()
        self.clicked.connect(self._on_click)
        self._apply_style()

    def _refresh_label(self):
        k = self._key
        if k.normal == "":          # spacer key
            self.setText("")
            self.setEnabled(False)
            self.setStyleSheet("background: transparent; border: none;")
            return
        top = k.shifted if k.shifted else ""
        bot = k.normal
        if top:
            self.setText(f"{top}\n{bot}")
        else:
            self.setText(bot)

    def _on_click(self):
        k = self._key
        if k.normal == "":
            return
        if k.typertask_token and k.hold_pair:
            # modifier hold/release toggle
            tok = self._hold_state.toggle(k.typertask_token)
            self._emit(tok)
            self._update_hold_style()
        elif k.typertask_token:
            self._emit(k.typertask_token)
        else:
            # literal character — use the normal label
            char = k.normal if k.normal != "⌫" else "\b"
            self._emit(k.normal)

    def _update_hold_style(self):
        k = self._key
        if k.typertask_token and self._hold_state.is_down(k.typertask_token):
            self.setStyleSheet(self.styleSheet() +
                               "background: #e07b39; color: #fff;")
        else:
            self._apply_style()

    def _apply_style(self):
        k = self._key
        if k.normal == "":
            return
        is_modifier = k.hold_pair or k.normal in ("Win", "Menu", "⇪")
        is_space = k.normal == " "
        base = """
            QPushButton {
                border-radius: 4px;
                font-size: 9px;
                font-family: 'JetBrains Mono', 'Consolas', monospace;
                padding: 1px 2px;
            }
            QPushButton:hover { opacity: 0.8; }
            QPushButton:pressed { padding-top: 3px; }
        """
        if is_modifier:
            color = "background: #3a4a5c; color: #c8d8e8;"
        elif is_space:
            color = "background: #2a3a4c; color: #8899aa;"
        else:
            color = "background: #1e2d3d; color: #d4e8f8;"
        self.setStyleSheet(base + color)
        self.setFont(QFont("JetBrains Mono", 8))


# ── Split hold key (Down / Up side by side) ───────────────────────────────────

class SplitModifierWidget(QWidget):
    """Two narrow buttons: {xdown} on the left, {xup} on the right."""
    UNIT = 32

    def __init__(self, key: Key, emit: Callable[[str], None], parent=None):
        super().__init__(parent)
        base = key.typertask_token.strip("{}").lower()   # e.g. "shift"
        down_tok = "{" + base + "down}"
        up_tok   = "{" + base + "up}"

        w = max(int(key.width * self.UNIT), 16)
        self.setFixedWidth(w)
        self.setFixedHeight(self.UNIT - 2)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)

        half = (w - 1) // 2

        label = key.normal          # "Shift", "Ctrl", "Alt"

        btn_down = QPushButton(f"{label}\n↓", self)
        btn_down.setFixedSize(half, self.UNIT - 2)
        btn_down.setToolTip(f"Inserta {down_tok}")
        btn_down.clicked.connect(lambda: emit(down_tok))
        self._style_btn(btn_down)

        btn_up = QPushButton(f"{label}\n↑", self)
        btn_up.setFixedSize(w - half - 1, self.UNIT - 2)
        btn_up.setToolTip(f"Inserta {up_tok}")
        btn_up.clicked.connect(lambda: emit(up_tok))
        self._style_btn(btn_up, is_up=True)

        layout.addWidget(btn_down)
        layout.addWidget(btn_up)

    @staticmethod
    def _style_btn(btn: QPushButton, is_up: bool = False):
        color = "#2d4a6a" if not is_up else "#1e3a50"
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {color};
                color: #a8c8e8;
                border-radius: 3px;
                font-size: 7px;
                font-family: 'JetBrains Mono', monospace;
                padding: 0px;
            }}
            QPushButton:hover {{ background: #3d6a8a; }}
            QPushButton:pressed {{ background: #e07b39; color: #fff; }}
        """)


# ── Row builder ───────────────────────────────────────────────────────────────

def _build_row(keys: list[Key], hold_state: _HoldState,
               emit: Callable[[str], None]) -> QWidget:
    row_w = QWidget()
    layout = QHBoxLayout(row_w)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(1)
    for key in keys:
        if key.hold_pair and key.typertask_token:
            layout.addWidget(SplitModifierWidget(key, emit))
        else:
            layout.addWidget(KeyButton(key, hold_state, emit))
    layout.addStretch()
    return row_w


# ── VirtualKeyboard ───────────────────────────────────────────────────────────

class VirtualKeyboard(QWidget):
    key_pressed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._hold_state = _HoldState()
        self._build_ui()

    def _emit(self, token: str):
        self.key_pressed.emit(token)

    def _build_ui(self):
        outer = QHBoxLayout(self)
        outer.setContentsMargins(4, 2, 4, 2)   # less vertical padding
        outer.setSpacing(4)

        # Main keyboard block
        kb_block = QVBoxLayout()
        kb_block.setSpacing(1)
        for row in ROWS:
            kb_block.addWidget(_build_row(row, self._hold_state, self._emit))
        outer.addLayout(kb_block)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet("color: #3a5a7a;")
        outer.addWidget(sep)

        # Navigation cluster
        nav_block = QVBoxLayout()
        nav_block.setSpacing(1)
        for row in NAV_CLUSTER:
            nav_block.addWidget(_build_row(row, self._hold_state, self._emit))
        outer.addLayout(nav_block)

        # Separator 2 — tighter spacing around it
        outer.addSpacing(2)
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.VLine)
        sep2.setStyleSheet("color: #3a5a7a;")
        outer.addWidget(sep2)
        outer.addSpacing(2)

        # Numpad cluster — no extra stretch, flush to bottom
        num_block = QVBoxLayout()
        num_block.setSpacing(1)
        num_block.setContentsMargins(0, 0, 0, 0)
        for row in NUMPAD_ROWS:
            num_block.addWidget(_build_row(row, self._hold_state, self._emit))
        outer.addLayout(num_block)

        self.setStyleSheet("background: #111e2d; border-radius: 8px;")
