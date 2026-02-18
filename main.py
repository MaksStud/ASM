import sys
import logging

from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit)
from PySide6.QtGui import QIcon, QFont

from runer import RunAssembler


class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ASM runer")
        self.resize(420, 300)
        self.setWindowIcon(QIcon(r"1658763190886.png"))

        layout = QVBoxLayout()

        self.input = QTextEdit()
        self.input.setPlaceholderText("Введіть код тут...")
        self.input.setMinimumSize(600, 600)
        self.input.setFont(QFont("Consolas", 11))
        layout.addWidget(self.input)

        self.button = QPushButton("Старт")
        self.button.setMinimumHeight(36)
        self.button.clicked.connect(self.process)
        layout.addWidget(self.button)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.setLayout(layout)

        self.setStyleSheet("""
            QWidget {
                background-color: #202124;
                color: white;
                font-family: Segoe UI;
                font-size: 14px;
            }
            QLineEdit, QTextEdit {
                background-color: #2d2f31;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton {
                background-color: #4a90e2;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357ae8;
            }
        """)

    def process(self):
        text: str = self.input.toPlainText()
        text = RunAssembler().run(f"{text}\n")
        self.output.clear()
        self.output.append(text)


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)


app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())
