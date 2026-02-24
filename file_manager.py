import logging
from PySide6.QtWidgets import QFileDialog

logger = logging.getLogger(__name__)


class ASMFileManager:
    def __init__(self, parent):
        self.parent = parent

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self.parent, "Open ASM file", "", "Assembly Files (*.asm *.txt);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.parent.input.setPlainText(f.read())
                logger.info(f"File loaded: {file_path}")
            except Exception as e:
                logger.error(f"Failed to load file: {e}")

    def save_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self.parent, "Save ASM file", "", "Assembly files (*.txt *.asm);;All files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.parent.input.toPlainText())
                logger.info(f"File saved: {file_path}")
            except Exception as e:
                logger.error(f"Failed to save file: {e}")
