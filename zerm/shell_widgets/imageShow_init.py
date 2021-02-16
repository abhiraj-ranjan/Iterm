from PyQt5 import QtWidgets, QtCore

class _image(QtWidgets.QPushButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def keyPressEvent(self, e):
        self.hide()
        self.parent.mainchild.commandRunnerFinished()
        self.parent.mainchild.show()
        self.parent.mainchild.setFocus()

    def mousePressEvent(self, event):
        self.parent.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QtCore.QPoint(event.globalPos()-self.parent.oldPos)
        self.parent.move(self.parent.x()+delta.x(), self.parent.y() + delta.y())
        self.parent.oldPos = event.globalPos()

def integrateWithShellClass(self):
    self.image = _image(self)
    self.image.setStyleSheet('background:transparent')
    self.image.resize(self.size().width()-10, self.size().height()-10)
    self.image.move(5, 5)
    self.image.hidden  = True
    self.image.hide()
