from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QRegExp
from shell_widgets import *
import shell_widgets

class WorkerSignals(QtCore.QObject):
    text     = QtCore.pyqtSignal(object)
    error    = QtCore.pyqtSignal()
    _error   = QtCore.pyqtSignal(object)
    finished = QtCore.pyqtSignal()
    _break   = QtCore.pyqtSignal()
    imageShow = QtCore.pyqtSignal(object)
    
class SideGrip(QtWidgets.QWidget):
    def __init__(self, parent, edge):
        QtWidgets.QWidget.__init__(self, parent)
        if edge == QtCore.Qt.LeftEdge:
            self.setCursor(QtCore.Qt.SizeHorCursor)
            self.resizeFunc = self.resizeLeft
        elif edge == QtCore.Qt.TopEdge:
            self.setCursor(QtCore.Qt.SizeVerCursor)
            self.resizeFunc = self.resizeTop
        elif edge == QtCore.Qt.RightEdge:
            self.setCursor(QtCore.Qt.SizeHorCursor)
            self.resizeFunc = self.resizeRight
        else:
            self.setCursor(QtCore.Qt.SizeVerCursor)
            self.resizeFunc = self.resizeBottom
        self.mousePos = None

    def resizeLeft(self, delta):
        window = self.window()
        width = max(window.minimumWidth(), window.width() - delta.x())
        geo = window.geometry()
        geo.setLeft(geo.right() - width)
        window.setGeometry(geo)

    def resizeTop(self, delta):
        window = self.window()
        height = max(window.minimumHeight(), window.height() - delta.y())
        geo = window.geometry()
        geo.setTop(geo.bottom() - height)
        window.setGeometry(geo)

    def resizeRight(self, delta):
        window = self.window()
        width = max(window.minimumWidth(), window.width() + delta.x())
        window.resize(width, window.height())

    def resizeBottom(self, delta):
        window = self.window()
        height = max(window.minimumHeight(), window.height() + delta.y())
        window.resize(window.width(), height)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.mousePos = event.pos()

    def mouseMoveEvent(self, event):
        if self.mousePos is not None:
            delta = event.pos() - self.mousePos
            self.resizeFunc(delta)

    def mouseReleaseEvent(self, event):
        self.mousePos = None

class borderFrame(QtWidgets.QWidget):
    _gripSize = 8
    def __init__(self, Style, app):
        super().__init__()
        
        self.app = app
        self.Style = Style
        self.lbl = QtWidgets.QLabel(self)
        
        if 'parent_bg_image' in Style:
            pix      = QtGui.QPixmap(self.Style['parent_bg_image'])
            self.lbl.setPixmap(pix)
            self.lbl.setScaledContents(True)
        self.lbl.setStyleSheet(self.styleSheet())

        if Style['window_startup_mode'] == 'CUSTOM_FRAMELESS_WINDOW':
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
            self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

            self._shade  = False
            self._maxed  = False

            self.btFrame = QtWidgets.QFrame(self)
            self.btFrame.setStyleSheet('background:transparent')
            self._lay    = QtWidgets.QHBoxLayout(self.btFrame)
            self._lay.setContentsMargins(0,0,0,0)
            self._lay.setSpacing(0)
            self.btFrame.setGeometry(QtCore.QRect(10, 10, 60, 10))

            self._close  = QtWidgets.QPushButton(self.btFrame)
            self._close.setMaximumSize(QtCore.QSize(8, 8))
            self._close.setText("")
            self._close.setObjectName("close")

            self.tmax    = QtWidgets.QPushButton(self.btFrame)
            self.tmax.setMaximumSize(QtCore.QSize(8, 8))
            self.tmax.setText("")
            self.tmax.setObjectName("pushButton_2")

            self.tmin    = QtWidgets.QPushButton(self.btFrame)
            self.tmin.setMaximumSize(QtCore.QSize(8, 8))
            self.tmin.setText("")
            self.tmin.setObjectName("pushButton_3")
            
            self.tshade  = QtWidgets.QPushButton(self.btFrame)
            self.tshade.setMaximumSize(QtCore.QSize(8, 8))
            self.tshade.setText("")
            self.tshade.setObjectName("pushButton_4")
            self.tshade.setCheckable(True)

            self._lay.addWidget(self._close)
            self._lay.addWidget(self.tmax)
            self._lay.addWidget(self.tmin)
            self._lay.addWidget(self.tshade)

            self._close.clicked.connect(self.close)
            self.tmax.clicked.connect(self.maxit)
            self.tmin.clicked.connect(self.showMinimized)
            self.tshade.released.connect(self.shademe)
            

        self.sideGrips = [
            SideGrip(self, QtCore.Qt.LeftEdge), 
            SideGrip(self, QtCore.Qt.TopEdge), 
            SideGrip(self, QtCore.Qt.RightEdge), 
            SideGrip(self, QtCore.Qt.BottomEdge), 
        ]
        # corner grips should be "on top" of everything, otherwise the side grips
        # will take precedence on mouse events, so we are adding them *after*;
        # alternatively, widget.raise_() can be used
        self.cornerGrips = [QtWidgets.QSizeGrip(self) for i in range(4)]

        self.loadModules()

    def loadModules(self):
        mods = shell_widgets.__all__
        import os
        globe = globals()
        for mod in mods:
            globe[mod].integrateWithShellClass(self)
            
    def initChild(self):
        lst    = self.children()
        for child in lst:
            if hasattr(child, 'forIdentParent'):
                self.mainchild = child

        print(self.mainchild.objectName())
        self.app.setApplicationDisplayName(self.mainchild.objectName())
        self.app.setApplicationName(self.mainchild.objectName())
        self.app.setApplicationVersion('1.0.0')

    @property
    def gripSize(self):
        return self._gripSize

    def setGripSize(self, size):
        if size == self._gripSize:
            return
        self._gripSize = max(2, size)
        self.updateGrips()

    def updateGrips(self):
        self.setContentsMargins(*[self.gripSize] * 4)

        outRect = self.rect()
        # an "inner" rect used for reference to set the geometries of size grips
        inRect = outRect.adjusted(self.gripSize, self.gripSize,
            -self.gripSize, -self.gripSize)

        # top left
        self.cornerGrips[0].setGeometry(
            QtCore.QRect(outRect.topLeft(), inRect.topLeft()))
        # top right
        self.cornerGrips[1].setGeometry(
            QtCore.QRect(outRect.topRight(), inRect.topRight()).normalized())
        # bottom right20
        self.cornerGrips[2].setGeometry(
            QtCore.QRect(inRect.bottomRight(), outRect.bottomRight()))
        # bottom left
        self.cornerGrips[3].setGeometry(
            QtCore.QRect(outRect.bottomLeft(), inRect.bottomLeft()).normalized())

        # left edge
        self.sideGrips[0].setGeometry(
            0, inRect.top(), self.gripSize, inRect.height())
        # top edge
        self.sideGrips[1].setGeometry(
            inRect.left(), 0, inRect.width(), self.gripSize)
        # right edge
        self.sideGrips[2].setGeometry(
            inRect.left() + inRect.width(), 
            inRect.top(), self.gripSize, inRect.height())
        # bottom edge
        self.sideGrips[3].setGeometry(
            self.gripSize, inRect.top() + inRect.height(), 
            inRect.width(), self.gripSize)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateGrips()
        if 'parent_bg_image' in self.Style:
            self.lbl.resize(self.size())
            self.lbl.setStyleSheet(self.styleSheet())
        self.image.resize(self.size().width()-10, self.size().height()-10)
        self.image.move(5, 5)
            
    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QtCore.QPoint(event.globalPos()-self.oldPos)
        self.move(self.x()+delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()    

    def shademe(self):
        sender = self.sender()
        if sender.isChecked():
            self.geo = self.saveGeometry()
            self.resize(QtCore.QSize(self.width(), 8))
            self._shade = True
            
        if not sender.isChecked():
            self.restoreGeometry(self.geo)
            self._shade = False

    def maxit(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

