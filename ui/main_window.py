"""
MainWindow — top-level application window.
Separates UI construction from logic; all logic lives in core/.
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStatusBar, QSplitter, QFrame,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon, QAction

from ui.keyboard_widget import VirtualKeyboard
from ui.editor_widget import SmartEditor
from ui.palette_widget import ShortcutPalette


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Typertask GUI  ·  v2")
        self.setMinimumSize(QSize(1100, 680))
        self._build_ui()
        self._connect_signals()
        self._apply_global_style()

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header bar ────────────────────────────────────────────────────────
        header = self._make_header()
        root.addWidget(header)

        # ── Keyboard area ─────────────────────────────────────────────────────
        self._keyboard = VirtualKeyboard()
        kb_frame = QFrame()
        kb_frame.setStyleSheet("background: #0d1820; border-bottom: 1px solid #1e3a55;")
        kb_layout = QHBoxLayout(kb_frame)
        kb_layout.setContentsMargins(8, 2, 8, 2)
        kb_layout.addWidget(self._keyboard)
        root.addWidget(kb_frame)

        # ── Middle: palette + editor ──────────────────────────────────────────
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(2)
        splitter.setStyleSheet("QSplitter::handle { background: #2a4a6a; }")

        self._palette = ShortcutPalette()
        splitter.addWidget(self._palette)

        editor_frame = QFrame()
        editor_frame.setStyleSheet("background: #080f18;")
        ef_layout = QVBoxLayout(editor_frame)
        ef_layout.setContentsMargins(10, 10, 10, 10)
        ef_layout.setSpacing(6)

        ed_label = QLabel("✏  Macro editor")
        ed_label.setStyleSheet("""
            color: #4a8abf;
            font-size: 11px;
            font-family: 'JetBrains Mono', monospace;
        """)
        ef_layout.addWidget(ed_label)

        self._editor = SmartEditor()
        ef_layout.addWidget(self._editor, 1)

        # Action buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self._btn_copy = self._make_action_btn("⎘  Copiar", "#1e5a8a")
        self._btn_clear = self._make_action_btn("✕  Limpiar", "#5a1e1e")
        btn_row.addStretch()
        btn_row.addWidget(self._btn_copy)
        btn_row.addWidget(self._btn_clear)
        ef_layout.addLayout(btn_row)

        splitter.addWidget(editor_frame)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        root.addWidget(splitter, 1)

        # ── Status bar ────────────────────────────────────────────────────────
        sb = QStatusBar()
        sb.setStyleSheet("""
            QStatusBar {
                background: #060e18;
                color: #3a6a8a;
                font-size: 9px;
                font-family: 'JetBrains Mono', monospace;
                border-top: 1px solid #1a3a5a;
            }
        """)
        sb.showMessage("Typertask GUI  ·  Escribe en el editor o usa el teclado virtual")
        self.setStatusBar(sb)
        self._status = sb

    def _make_header(self) -> QWidget:
        w = QWidget()
        w.setFixedHeight(42)
        w.setStyleSheet("background: #060e18; border-bottom: 1px solid #1a3a5a;")
        lay = QHBoxLayout(w)
        lay.setContentsMargins(14, 0, 14, 0)

        logo = QLabel("⌨  <b>Typertask</b>  GUI")
        logo.setStyleSheet("""
            color: #5aafd4;
            font-size: 15px;
            font-family: 'JetBrains Mono', monospace;
        """)
        lay.addWidget(logo)
        lay.addStretch()

        hint = QLabel("↑ Teclado virtual  ·  Escribe { para autocompletar")
        hint.setStyleSheet("color: #2a5a7a; font-size: 10px; font-family: 'JetBrains Mono', monospace;")
        lay.addWidget(hint)
        return w

    @staticmethod
    def _make_action_btn(text: str, color: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedHeight(32)
        btn.setFont(QFont("JetBrains Mono", 10))
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {color};
                color: #c8e8ff;
                border: 1px solid #4a7aaa;
                border-radius: 6px;
                padding: 4px 16px;
                font-family: 'JetBrains Mono', monospace;
            }}
            QPushButton:hover {{  }}
            QPushButton:pressed {{ padding-top: 6px; }}
        """)
        return btn

    # ── Signals ───────────────────────────────────────────────────────────────

    def _connect_signals(self):
        self._keyboard.key_pressed.connect(self._on_key)
        self._palette.shortcut_clicked.connect(self._on_key)
        self._btn_copy.clicked.connect(self._copy_to_clipboard)
        self._btn_clear.clicked.connect(self._editor.clear)

    def _on_key(self, token: str):
        self._editor.insert_token(token)
        self._status.showMessage(f"Insertado: {token}", 2000)

    def _copy_to_clipboard(self):
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(self._editor.toPlainText())
        self._status.showMessage("✓ Copiado al portapapeles", 2000)

    # ── Style ─────────────────────────────────────────────────────────────────

    def _apply_global_style(self):
        self.setStyleSheet("""
            QMainWindow { background: #080f18; }
            QToolTip {
                background: #0d1b2a;
                color: #90c8e8;
                border: 1px solid #3a6a9a;
                font-family: 'JetBrains Mono', monospace;
                font-size: 10px;
                padding: 4px;
            }
        """)
