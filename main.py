import sys
import logging
import os
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QTextEdit, QDialog, QFileDialog, QTextBrowser)
from PySide6.QtGui import QIcon, QFont

from runer import RunAssembler
from file_manager import ASMFileManager


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class LogEmitter(QObject):
    sigLog = Signal(str)


class QLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.emitter = LogEmitter()

    def emit(self, record):
        msg = self.format(record)
        self.emitter.sigLog.emit(msg)


class LogWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Логи програми")
        self.resize(600, 400)
        layout = QVBoxLayout(self)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Consolas", 10))
        layout.addWidget(self.text_edit)

    @Slot(str)
    def append_log(self, msg):
        self.text_edit.append(msg)


class HelpWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Help - User Guide")
        self.resize(720, 520)

        layout = QVBoxLayout(self)

        self.help_text = QTextBrowser()
        self.help_text.setOpenExternalLinks(True)
        self.help_text.setFont(QFont("Segoe UI", 10))
        self.help_text.setHtml("""
            <h2>ASM Runner - User Guide</h2>
            <p>This app lets you write, run, and compile x86-64 assembly code.</p>

            <h3>Quick Start</h3>
            <ol>
              <li>Write or paste assembly code in the main editor.</li>
              <li>Click <b>Run</b> to execute code in the emulator.</li>
              <li>Check output in the bottom panel.</li>
            </ol>

            <h3>Top Buttons</h3>
            <ul>
              <li><b>Open</b>: Load a <code>.asm</code> or <code>.txt</code> file into the editor.</li>
              <li><b>Save</b>: Save current editor content to file.</li>
              <li><b>Logs</b>: Open detailed runtime and error logs.</li>
              <li><b>Help</b>: Open this guide.</li>
            </ul>

            <h3>Compile</h3>
            <ul>
              <li>Click <b>Compile</b> to assemble source code without running it.</li>
              <li>Choose output format:
                <ul>
                  <li><b>Binary (*.bin)</b> for raw machine code bytes.</li>
                  <li><b>Text (*.txt)</b> for human-readable hex output.</li>
                </ul>
              </li>
            </ul>

            <h3>Run</h3>
            <ul>
              <li>Click <b>Run</b> to emulate your code.</li>
              <li>The program captures output from Linux <code>write</code> syscall (<code>rax=1</code>).</li>
              <li>Execution stops on <code>exit</code> syscall (<code>rax=60</code>).</li>
            </ul>

            <h3>Troubleshooting</h3>
            <ul>
              <li>If you see <b>Compilation error</b>, review syntax and instruction operands.</li>
              <li>If output is empty, ensure your code writes to stdout before exiting.</li>
              <li>Use <b>Logs</b> for detailed diagnostics.</li>
            </ul>
        """)
        layout.addWidget(self.help_text)


formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)


class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.file_manager = ASMFileManager(self)
        self.log_window = LogWindow(self)
        self.help_window = HelpWindow(self)
        self.gui_logger = QLogHandler()
        self.gui_logger.setFormatter(formatter)
        self.gui_logger.emitter.sigLog.connect(self.log_window.append_log)

        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(self.gui_logger)

        self.init_ui()
        self.load_styles()

    def init_ui(self):
        self.setWindowTitle("ASM runner")
        self.resize(800, 600)
        
        icon_path = resource_path("1658763190886.png")
        self.setWindowIcon(QIcon(icon_path))

        layout = QVBoxLayout(self)
        top_bar = QHBoxLayout()

        self.open_btn = QPushButton("Open")
        self.open_btn.setObjectName("LogButton")
        self.open_btn.setFixedSize(80, 24)
        self.open_btn.clicked.connect(self.file_manager.open_file)

        self.save_btn = QPushButton("Save")
        self.save_btn.setObjectName("LogButton")
        self.save_btn.setFixedSize(80, 24)
        self.save_btn.clicked.connect(self.file_manager.save_file)

        self.log_button = QPushButton("Logs")
        self.log_button.setObjectName("LogButton")
        self.log_button.setFixedSize(60, 24)
        self.log_button.clicked.connect(self.log_window.show)

        self.help_button = QPushButton("Help")
        self.help_button.setObjectName("LogButton")
        self.help_button.setFixedSize(60, 24)
        self.help_button.clicked.connect(self.help_window.show)

        top_bar.addWidget(self.help_button)
        top_bar.addWidget(self.log_button)
        top_bar.addWidget(self.open_btn)
        top_bar.addWidget(self.save_btn)
        top_bar.addStretch()

        layout.addLayout(top_bar)

        self.input = QTextEdit()
        self.input.setPlaceholderText("Enter the code here...")
        self.input.setMinimumSize(600, 400)
        self.input.setFont(QFont("Consolas", 11))
        layout.addWidget(self.input)

        btn_row = QHBoxLayout()

        self.compile_btn = QPushButton("Compile")
        self.compile_btn.setMinimumHeight(40)
        self.compile_btn.clicked.connect(self.compile)
        btn_row.addWidget(self.compile_btn)

        self.button = QPushButton("Run")
        self.button.setMinimumHeight(40)
        self.button.clicked.connect(self.process)
        btn_row.addWidget(self.button)

        layout.addLayout(btn_row)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setMaximumHeight(150)
        layout.addWidget(self.output)

    def load_styles(self):
        style_path = resource_path("style.qss")
        try:
            with open(style_path, "r", encoding="utf-8") as f:
                style = f.read()
                self.setStyleSheet(style)
                self.log_window.setStyleSheet(style)
                self.help_window.setStyleSheet(style)
        except Exception as e:
            logger.error(f"Could not load stylesheet: {e}")

    def compile(self):
        text = self.input.toPlainText()
        try:
            machine_code, count = RunAssembler().compile(f"{text}\n")
        except Exception as e:
            self.output.setPlainText(f"Compilation error: {e}")
            logger.exception("Compilation failed")
            return

        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, "Save compiled output", "",
            "Binary files (*.bin);;Text files (*.txt)"
        )
        if not file_path:
            return

        try:
            if selected_filter == "Text files (*.txt)":
                hex_str = ' '.join(f'{b:02X}' for b in machine_code)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Instructions: {count}\n")
                    f.write(f"Machine code: {hex_str}\n")
            else:
                with open(file_path, 'wb') as f:
                    f.write(machine_code)

            self.output.setPlainText(f"Compiled {count} instruction(s) -> {file_path}")
            logger.info(f"Compiled output saved to {file_path}")
        except Exception as e:
            self.output.setPlainText(f"Error saving file: {e}")
            logger.exception("Failed to save compiled output")

    def process(self):
        text = self.input.toPlainText()
        try:
            output = RunAssembler().run(f"{text}\n")
            self.output.setPlainText(output)
            logger.info("Code executed successfully")
        except Exception as e:
            self.output.setPlainText(f"Error: {e}")
            logger.exception("Execution failed")


if __name__ == "__main__":
    logger.info("Starting Qt application.")
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
