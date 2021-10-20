from typing import Mapping
import Screen
from PyQt5.QtWidgets import QApplication


if __name__ == "__main__":
    app = QApplication([])
    terminalUI = Screen.screen()
    terminalUI.show()
    app.exec()