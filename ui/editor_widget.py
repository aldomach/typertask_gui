"""
SmartEditor — QPlainTextEdit with inline Typertask autocomplete.

Autocomplete fires when the user types any character.
The popup shows matching shortcuts; pressing Tab/Enter inserts the selected one.
"""
from __future__ import annotations
from typing import List

from PySide6.QtWidgets import (
    QPlainTextEdit, QListWidget, QListWidgetItem,
    QWidget, QVBoxLayout, QLabel,
)
from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtGui import QKeyEvent, QFont, QTextCursor

from core.shortcuts import get_suggestions, Shortcut


class AutocompletePopup(QListWidget):
    """Floating list that shows suggestions."""
    item_chosen = Signal(str)   # emits the token to insert

    MAX_VISIBLE = 8
    ROW_H = 28

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        self.setStyleSheet("""
            QListWidget {
                background: #0d1b2a;
                border: 1px solid #3a7abf;
                border-radius: 6px;
                outline: none;
                font-family: 'JetBrains Mono', 'Consolas', monospace;
                font-size: 11px;
                color: #c8e0f8;
            }
            QListWidget::item { padding: 3px 10px; border-radius: 4px; }
            QListWidget::item:selected { background: #1d4e8a; color: #ffffff; }
            QListWidget::item:hover { background: #16375c; }
        """)
        self.setFont(QFont("JetBrains Mono", 10))
        self.itemActivated.connect(self._on_activate)

    def show_suggestions(self, suggestions: List[Shortcut], global_pos: QPoint):
        self.clear()
        for s in suggestions:
            text = f"{s.token:<22}  {s.description}"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, s.token)
            self.addItem(item)
        if self.count():
            self.setCurrentRow(0)
            visible = min(self.count(), self.MAX_VISIBLE)
            self.setFixedHeight(visible * self.ROW_H + 4)
            self.setFixedWidth(380)
            self.move(global_pos)
            self.show()
            self.raise_()
        else:
            self.hide()

    def _on_activate(self, item: QListWidgetItem):
        self.item_chosen.emit(item.data(Qt.UserRole))
        self.hide()

    def select_next(self):
        r = self.currentRow()
        self.setCurrentRow(min(r + 1, self.count() - 1))

    def select_prev(self):
        r = self.currentRow()
        self.setCurrentRow(max(r - 1, 0))

    def accept_current(self) -> str | None:
        item = self.currentItem()
        if item:
            tok = item.data(Qt.UserRole)
            self.hide()
            return tok
        return None


class SmartEditor(QPlainTextEdit):
    """Plain-text editor with Typertask autocomplete."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._popup = AutocompletePopup()
        self._popup.item_chosen.connect(self._insert_token)
        self._query = ""   # current word being typed

        self.setFont(QFont("JetBrains Mono", 12))
        self.setStyleSheet("""
            QPlainTextEdit {
                background: #0a1520;
                color: #d4f0ff;
                border: 1px solid #2a4a6a;
                border-radius: 6px;
                padding: 8px;
                selection-background-color: #1d4e8a;
                font-family: 'JetBrains Mono', 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        self.setPlaceholderText(
            "Escribe aquí tu macro… escribe { para autocompletar atajos Typertask"
        )
        self.textChanged.connect(self._on_text_changed)

    # ── Autocomplete trigger ──────────────────────────────────────────────────

    def _current_word(self) -> str:
        """
        Returns the fragment the user is currently typing, measured from the
        cursor back to the nearest word-break.

        Word-breaks are: whitespace, newline, OR the closing '}' of a previously
        completed Typertask token.  This means after inserting '{enter}' the next
        character immediately starts a new fragment — no space required.
        """
        cursor = self.textCursor()
        text = self.toPlainText()
        pos = cursor.position()
        start = pos
        while start > 0:
            c = text[start - 1]
            # Stop at whitespace or right after a closing brace (end of a token)
            if c in (" ", "\n", "\t", "\r") or c == "}":
                break
            start -= 1
        return text[start:pos]

    def _word_start(self) -> int:
        """Return the start index of the current word (mirrors _current_word logic)."""
        cursor = self.textCursor()
        text = self.toPlainText()
        pos = cursor.position()
        start = pos
        while start > 0:
            c = text[start - 1]
            if c in (" ", "\n", "\t", "\r") or c == "}":
                break
            start -= 1
        return start

    def _on_text_changed(self):
        word = self._current_word()
        self._query = word
        if len(word) >= 1:
            suggestions = get_suggestions(word)
            if suggestions:
                # Show popup just below the cursor
                rect = self.cursorRect()
                global_pos = self.viewport().mapToGlobal(
                    QPoint(rect.left(), rect.bottom() + 4)
                )
                self._popup.show_suggestions(suggestions, global_pos)
                return
        self._popup.hide()

    def _insert_token(self, token: str):
        """Replace the current partial word with the chosen token."""
        cursor = self.textCursor()
        pos = cursor.position()
        start = self._word_start()
        cursor.setPosition(start)
        cursor.setPosition(pos, QTextCursor.KeepAnchor)
        cursor.insertText(token)
        self.setTextCursor(cursor)
        self._popup.hide()

    def insert_token(self, token: str):
        """Public API: insert token at cursor (called by keyboard/buttons)."""
        self.insertPlainText(token)
        self.setFocus()

    # ── Keyboard navigation of popup ─────────────────────────────────────────

    def keyPressEvent(self, event: QKeyEvent):
        if self._popup.isVisible():
            if event.key() in (Qt.Key_Down,):
                self._popup.select_next()
                return
            if event.key() in (Qt.Key_Up,):
                self._popup.select_prev()
                return
            if event.key() in (Qt.Key_Tab, Qt.Key_Return, Qt.Key_Enter):
                tok = self._popup.accept_current()
                if tok:
                    self._insert_token(tok)
                    return
            if event.key() == Qt.Key_Escape:
                self._popup.hide()
                return
        super().keyPressEvent(event)

    def focusOutEvent(self, event):
        # hide popup unless focus went to the popup itself
        if not self._popup.underMouse():
            self._popup.hide()
        super().focusOutEvent(event)
