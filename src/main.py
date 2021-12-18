from PyQt5 import QtWidgets
import Screen as screen

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    terminal = screen.screen()
    terminal.show()
    app.exec()