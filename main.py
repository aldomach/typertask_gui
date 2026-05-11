"""
Typertask GUI v2 — entry point.
Run: python main.py
"""
import sys
import os

# Ensure project root is on the path (for imports like core.*, ui.*)
sys.path.insert(0, os.path.dirname(__file__))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Typertask GUI")
    app.setOrganizationName("Typertask")

    # Prefer a monospace font for the whole app
    default_font = QFont("JetBrains Mono", 10)
    default_font.setHintingPreference(QFont.HintingPreference.PreferFullHinting)
    app.setFont(default_font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
