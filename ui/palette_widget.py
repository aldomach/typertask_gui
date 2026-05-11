"""
ShortcutPalette — categorised sidebar of Typertask shortcuts.
"""
from __future__ import annotations
from typing import Callable

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QScrollArea, QLabel, QFrame, QSizePolicy,
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont

from core.shortcuts import SHORTCUTS, Shortcut, category_order


CATEGORY_ICONS = {
    "modifier":   "⌨",
    "hold":       "⏬",
    "navigation": "🧭",
    "editing":    "✏️",
    "timing":     "⏱",
    "command":    "▶",
    "datetime":   "📅",
    "media":      "🔊",
    "numpad":     "🔢",
    "function":   "Fn",
}

CATEGORY_LABELS = {
    "modifier":   "Modificadores",
    "hold":       "Mantener / Soltar",
    "navigation": "Navegación",
    "editing":    "Edición",
    "timing":     "Delays",
    "command":    "Comandos",
    "datetime":   "Fecha / Hora",
    "media":      "Multimedia",
    "numpad":     "Teclado Numérico",
    "function":   "Teclas de Función",
}


class _ShortcutBtn(QPushButton):
    def __init__(self, shortcut: Shortcut, emit: Callable[[str], None]):
        super().__init__(shortcut.label)
        self.setToolTip(f"{shortcut.token}\n{shortcut.description}")
        self.setFixedHeight(30)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.clicked.connect(lambda: emit(shortcut.token))
        self.setStyleSheet("""
            QPushButton {
                background: #152030;
                color: #90c0e0;
                border: 1px solid #2a4a6a;
                border-radius: 5px;
                font-size: 10px;
                font-family: 'JetBrains Mono', monospace;
                padding: 2px 6px;
                text-align: left;
            }
            QPushButton:hover {
                background: #1e3a55;
                color: #d4f0ff;
                border-color: #4a8abf;
            }
            QPushButton:pressed {
                background: #e07b39;
                color: #fff;
            }
        """)


class ShortcutPalette(QWidget):
    shortcut_clicked = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        title = QLabel("Atajos Typertask")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            color: #5aafd4;
            font-size: 12px;
            font-weight: bold;
            font-family: 'JetBrains Mono', monospace;
            padding: 6px 0;
            background: #0d1b2a;
            border-bottom: 1px solid #2a4a6a;
        """)
        outer.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: #0d1b2a; }
            QScrollBar:vertical { width: 6px; background: #0d1b2a; }
            QScrollBar::handle:vertical { background: #2a4a6a; border-radius: 3px; }
        """)

        container = QWidget()
        container.setStyleSheet("background: #0d1b2a;")
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(6, 6, 6, 6)
        vbox.setSpacing(8)

        # Group by category — only show shortcuts NOT already on the virtual keyboard
        by_cat: dict[str, list[Shortcut]] = {}
        for s in SHORTCUTS:
            if not s.on_keyboard:
                by_cat.setdefault(s.category, []).append(s)

        for cat in category_order():
            if cat not in by_cat:
                continue
            icon = CATEGORY_ICONS.get(cat, "•")
            label_text = CATEGORY_LABELS.get(cat, cat.title())

            hdr = QLabel(f"{icon}  {label_text}")
            hdr.setStyleSheet("""
                color: #4a8abf;
                font-size: 10px;
                font-weight: bold;
                font-family: 'JetBrains Mono', monospace;
                padding: 2px 4px;
                border-bottom: 1px solid #1e3a55;
            """)
            vbox.addWidget(hdr)

            # Wrap buttons in a flow-ish grid (2 per row)
            row_w = QWidget()
            row_l = QHBoxLayout(row_w)
            row_l.setContentsMargins(0, 0, 0, 0)
            row_l.setSpacing(4)
            row_l.setAlignment(Qt.AlignLeft)

            for i, s in enumerate(by_cat[cat]):
                btn = _ShortcutBtn(s, self.shortcut_clicked.emit)
                row_l.addWidget(btn)
                if (i + 1) % 2 == 0 and i + 1 < len(by_cat[cat]):
                    vbox.addWidget(row_w)
                    row_w = QWidget()
                    row_l = QHBoxLayout(row_w)
                    row_l.setContentsMargins(0, 0, 0, 0)
                    row_l.setSpacing(4)
                    row_l.setAlignment(Qt.AlignLeft)

            row_l.addStretch()
            vbox.addWidget(row_w)

        vbox.addStretch()
        scroll.setWidget(container)
        outer.addWidget(scroll)

        self.setFixedWidth(220)
        self.setStyleSheet("background: #0d1b2a;")
