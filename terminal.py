from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter
import syntax, sys, os, subprocess, shlex

keymap = {}
for key, value in vars(QtCore.Qt).items():
    if isinstance(value, QtCore.Qt.Key):
        keymap[value] = key.partition('_')[2]

modmap = {
    QtCore.Qt.ControlModifier: keymap[QtCore.Qt.Key_Control],
    QtCore.Qt.AltModifier: keymap[QtCore.Qt.Key_Alt],
    QtCore.Qt.ShiftModifier: keymap[QtCore.Qt.Key_Shift],
    QtCore.Qt.MetaModifier: keymap[QtCore.Qt.Key_Meta],
    QtCore.Qt.GroupSwitchModifier: keymap[QtCore.Qt.Key_AltGr],
    QtCore.Qt.KeypadModifier: keymap[QtCore.Qt.Key_NumLock],
    }

def keyevent_to_string(event):
    sequence = []
    for modifier, text in modmap.items():
        if event.modifiers() & modifier:
            sequence.append(text)
    key = keymap.get(event.key(), event.text())
    if key not in sequence:
        sequence.append(key)
    return '+'.join(sequence)

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

class WorkerSignals(QtCore.QObject):
    text     = QtCore.pyqtSignal(object)
    error    = QtCore.pyqtSignal()
    _error   = QtCore.pyqtSignal(object)
    finished = QtCore.pyqtSignal()
    _break   = QtCore.pyqtSignal()

class commandRunner(QtCore.QObject):
    def __init__(self, command, *args, **kwargs):
        super().__init__()
        self.args    = args
        self.kwargs  = kwargs
        self.command = command
        self.breakthebond = False
        self.signals = WorkerSignals()
        
    QtCore.pyqtSlot()
    def run(self):
        try:
            from subprocess import Popen, PIPE, DEVNULL, STDOUT
            self.process = Popen(self.command, stdout=PIPE, stderr=STDOUT, shell=True)
            while True:
                line = self.process.stdout.readline().rstrip()
                if self.process.poll() == 0:
                    self.signals.finished.emit()
                    return
                self.signals.text.emit(line)

        except Exception as e:
            self.signals._error.emit(bytes(str(e), 'utf-8'))

    def _break_(self):
        self.breakthebond = True

class plain(QtWidgets.QTextEdit):
    def __init__(self, parent, Style):
        super().__init__(parent)
        self.parent         = parent
        self.Style          = Style
        self.forechar       = QtGui.QTextCharFormat()
        self.prev           = 0
        self.grabbedEditor  = False
        self.waitforobject  = False
        self.prompt         = os.getcwd() + '\n❯ '
        self.cleared        = False
        self.Signals        = WorkerSignals()
        self._waitforobject = self.Signals.finished
        self._back_re       = 0
        self._waitforobject.connect(self.restorehtml)

        vbar = self.verticalScrollBar()
        vbar.hide()
        hbar = self.horizontalScrollBar()
        hbar.hide()
        a = os.getcwd()+'\n'+'❯ '
        cur = self.textCursor()
        cur.insertText(a)
        self.setTextCursor(cur)
        self.startedEdting = False
        self.test = ''

    def lenByIter(self, lists):
        init = 0
        for i in lists:
            init += len(i)
        return init

    def keyPressEvent(self, e):
        self._stop = False
        self.e = e
        cur = self.textCursor()
        self.cur = cur
            
        try:
            if self.waitforobject:
                self._waitforobject.emit()
                self.setReadOnly(False)
                self.waitforobject = False
                self._stop = True
                
            if self.grabbedEditor :
                if keyevent_to_string(e) == 'Control+C' or keyevent_to_string(e) == 'Control+D':
                    self.commandrunnerThread.quit()
                    self.commandRunnerFinished()
                    self.grabbedEditor= False
                self._stop = True
                return

            if keyevent_to_string(e) == 'Backspace':
                cur.select(cur.BlockUnderCursor)
                if  ' ❯ ' == cur.selectedText():
                   self._stop = True
            if keyevent_to_string(e) == 'Return':
                if self.toPlainText().split('❯ ')[-1].strip() == '': return
                self.grabbedEditor = True
                if self.commandCheck(self.toPlainText().split('❯ ')[-1]) : return
                self.commandrunnerThread = QtCore.QThread()
                self.commandrunner = commandRunner(self.toPlainText().split('❯ ')[-1])
                self.commandrunner.signals._error.connect(self.commandRunner_Error)
                self.commandrunner.signals._break.connect(self.commandrunner._break_)
                self.commandrunner.signals.text.connect(self.commandRunnerText)
                self.commandrunner.signals.finished.connect(self.commandRunnerFinished)
                self.commandrunner.moveToThread(self.commandrunnerThread)
                self.commandrunnerThread.started.connect(self.commandrunner.run)
                self.commandrunner.signals.finished.connect(self.commandrunner.deleteLater)
                self.commandrunner.signals.finished.connect(self.commandrunnerThread.quit)
                self.commandrunnerThread.finished.connect(self.commandrunnerThread.deleteLater)
                self.commandrunnerThread.start()

            if not self._stop:
                super().keyPressEvent(self.e)
        except Exception as e:
            self.commandRunner_Error(bytes(str(e), encoding='utf-8'))

    def keyReleaseEvent(self, e):
        pass

    def commandCheck(self, command):
        if command == 'ls':
            cur = self.textCursor()
            self.cur.insertText('\n', self.forechar)
            dirchar = QtGui.QTextCharFormat()
            dirchar.setForeground(QtGui.QColor(self.Style['dircolor']))
            filchar = QtGui.QTextCharFormat()
            filchar.setForeground(QtGui.QColor(self.Style['filecolor']))
            dirs, files = [],[]
            
            for e in os.listdir():
                if os.path.isdir(os.path.join(os.getcwd(), e)):
                    dirs.append(e)
                if os.path.isfile(os.path.join(os.getcwd(), e)):
                    files.append(e)

            dirs.sort()
            files.sort()
            for e in dirs:
                self.cur.insertText(e+'\t', dirchar)
            for e in files:
                self.cur.insertText(e+'\t', filchar)

            self.setTextCursor(cur)
            self.commandRunnerFinished()
            return True

        if 'imageShow' == command.strip().split()[0]:
            cur = self.textCursor()
            if os.path.exists(os.path.abspath(command.strip().split()[1])):
                if os.path.isfile(os.path.abspath(command.strip().split()[1])):
                    self.html = self.toHtml()
                    self.clear()
                    img = QtGui.QImage()
                    img.load(os.path.abspath(command.strip().split()[1]))
                    img.scaled(self.parent.width(), self.parent.height())
                    cur.insertImage(img)
                    self.setReadOnly(True)
                    self.waitforobject = True
                else:
                    cur.setPosition(len(self.toPlainText()))
                    self.cur = self.textCursor()
                    self.cur.insertText('\n')
                    self.commandRunner_Error(bytes(str('imageShow: '+os.path.abspath(command.strip().split()[1]) + ' is not a file'), 'ascii'))
                    self.commandRunnerFinished()
            else:
                cur.setPosition(len(self.toPlainText()))
                self.cur = self.textCursor()
                self.cur.insertText('\n')
                self.commandRunner_Error(bytes(str('imageShow: path doesn\'t exist'), 'utf-8'))
                self.commandRunnerFinished()        
            return True

        if 'clear' == command.strip():
            self.clear()
            cur = self.textCursor()
            cur.insertText(self.prompt, self.forechar)
            self.setTextCursor(cur)
            self.cleared = True
            self.grabbedEditor = False
            self.ensureCursorVisible()
            return True

        _cmd = command.strip()
        if 'cd' == _cmd[:2] and command.strip()[2] == ' ':
            _ = _cmd.split('cd')[1]
            _ = _.strip()
            if _[0] == _[-1] == '"' or _[0] == _[-1] == '"':
                _ = _[1:-1]
            try:
                os.chdir(_)
            except Exception as  e:
                cur = self.textCursor()
                cur.setPosition(len(self.toPlainText()))
                self.cur = self.textCursor()
                self.cur.insertText('\n')
                self.commandRunner_Error(bytes(str(e), 'utf-8'))
            self.commandRunnerFinished()
            return True

        if 'python' == _cmd[:6] and ' ' == _cmd[6]:
            _ = _cmd[7:]
            cur = self.textCursor()
            cur.insertText('\n')

            self.sig = WorkerSignals()
            self.pythonThread = QtCore.QThread()
            self._ = _
            self.pythonThread.started.connect(self._python_)
            self.sig.finished.connect(self.pythonThread.quit)
            self.sig.finished.connect(self.commandRunnerFinished)
            self.pythonThread.finished.connect(self.pythonThread.deleteLater)
            self.pythonThread.start()
            return True
        return False

    def _python_(self):
        try:
            exec(self._, {'print':self._print})
        except Exception as e:
            print(e)
        finally :
            self.sig.finished.emit()

    def _print(self, cmd):
        print(cmd)
        cur = self.textCursor()
        cur.insertText(str(cmd)+'\n')
        self.setTextCursor(cur)

    def restorehtml(self):
        self.clear()
        self.insertHtml(self.html)
        self.commandRunnerFinished()
        self.grabbedEdtor = False

    def commandRunnerError(self):
        pass

    def commandRunner_Error(self, e):
        cur = self.textCursor()
        cur.setPosition(len(self.toPlainText()))
        char = QtGui.QTextCharFormat()
        char.setForeground(QtGui.QColor(self.Style['error']))
        cur.insertText(e.decode('utf-8'), char)
        self.setTextCursor(cur)
        #self.commandRunnerFinished()

    def commandRunnerText(self, e):
        cur = self.textCursor()
        cur.setPosition(len(self.toPlainText()))
        try:
            self.test += e.decode('utf-8')
            self.cur.insertText(u'{0}'.format(e.decode('utf-8')) + '\n', self.forechar)
        except Exception  as e:
            print(e)
            self.cur.insertText(str(e)[1:-1], self.forechar)
        self.setTextCursor(cur)
        self.ensureCursorVisible()
        
    def commandRunnerFinished(self, *args):
        self.prompt = os.getcwd() + '\n❯ '
        cur = self.textCursor()
        self.cur.insertText('\n\n'+self.prompt, self.forechar)
        self.setTextCursor(self.cur)
        self.grabbedEditor = False
        self.ensureCursorVisible()
        
    def pushEditorOutput(self, e):
        pass

class borderFrame(QtWidgets.QWidget):
    _gripSize = 8
    def __init__(self, Style):
        QtWidgets.QMainWindow.__init__(self)

        if Style['flag'] == 'CUSTOM_FRAMELESS_WINDOW':
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

            self._shade  = False
            self._maxed  = False

            self.btFrame = QtWidgets.QFrame(self)
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
        # bottom right
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
        QtWidgets.QMainWindow.resizeEvent(self, event)
        self.updateGrips()

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

def loadConf(path):
    if not os.path.exists(path): return 0
    import json
    with open('conf') as file:
        _json = json.load(file)
    return _json

if __name__ == '__main__':
    conf = loadConf(os.path.join(os.getcwd(), 'conf'))
    app    = QtWidgets.QApplication([])

    Style = {'dircolor':conf['dircolor'], 'filecolor':conf['filecolor'], 'error':conf['error'], 'flag':conf['window_startup_mode']}
    
    widget = borderFrame(Style)
    layout = QtWidgets.QVBoxLayout(widget)

    layout.setContentsMargins(int(conf['margin-Left']), int(conf['margin-Top']), int(conf['margin-Right']), int(conf['margin-Bottom']))

    editor = plain(widget, Style)
    layout.addWidget(editor)
    widget.resize(QtCore.QSize(int(conf['window_size'].split('x')[0]), int(conf['window_size'].split('x')[1])))

    widget.setStyleSheet(conf['parent_Ss'])
    editor.setStyleSheet(conf['editor_Ss'])
    widget._close.setStyleSheet(conf['window_closebt_styleSheet'])
    widget.tmin.setStyleSheet(conf['window_minbt_styleSheet'])
    widget.tshade.setStyleSheet(conf['window_shadebt_styleSheet'])
    widget.tmax.setStyleSheet(conf['window_maxbt_styleSheet'])

    high = syntax.PythonHighlighter(editor.document())
    widget.show()
    app.exec()
