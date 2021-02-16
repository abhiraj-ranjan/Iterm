from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter
import sys, os, subprocess, json
from .util import *

class Constants:
    def __init__(self):
        pass

class WorkerSignals(QtCore.QObject):
    text     = QtCore.pyqtSignal(object)
    error    = QtCore.pyqtSignal()
    _error   = QtCore.pyqtSignal(object)
    finished = QtCore.pyqtSignal()
    _break   = QtCore.pyqtSignal()
    imageShow = QtCore.pyqtSignal(object)

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
            from subprocess import Popen, PIPE, STDOUT
            process = Popen(self.command, stdout=PIPE, stderr=PIPE, shell=True)
            while True:
                if self.breakthebond :
                    self.signals.finished.emit()
                    break
                line = process.stdout.readline()
                if process.poll() is not None:
                    if process.poll() !=0:
                        self.signals._error.emit(bytes('Error['+str(process.poll())+'] ', 'utf-8')+process.stderr.read())
                    self.signals.finished.emit()
                    break
                if line:
                    self.signals.text.emit(line)

        except Exception as e:
            print(e)
            self.signals._error.emit(bytes(str(e), 'utf-8'))

    def _break_(self):
        self.breakthebond = True

class QZerm(QtWidgets.QTextEdit):
    def __init__(self, parent, Style):
        super().__init__(parent)
        self.setObjectName('QZerm')
        
        self.constant         = Constants()
        self.parent           = parent
        self.Style            = Style
        self.waitforobject    = False
        self.Signals          = WorkerSignals()
        self.imageShow        = self.Signals.imageShow
        self._waitforobject   = self.Signals.finished
        self._back_re         = 0
        self.constant.cleared = False
        self.startedEdting    = False
        self.constant.path    = os.environ['PATH']
        self.parent           = self.parentWidget()
        self.forIdentParent   = "main"

        self._waitforobject.connect(self.restorehtml)
        
        if self.Style['vbar'] == 'hide':
            vbar = self.verticalScrollBar()
            vbar.hide()
        if self.Style['hbar'] == 'hide':
            hbar = self.horizontalScrollBar()
            hbar.hide()

        if 'prompt' in self.Style:
            _ = self.Style['prompt'].split('|')
            self.constant.promptMenu = []
            for i in _:
                self.makeprompt(i.strip())
            self.buildprompt()
        
    def makeprompt(self, tomake):
        self.constant.promptMenu.append(tomake)

        if tomake == 'node':
            self.constant.beforeloginnodechar = QtGui.QTextCharFormat()
            self.constant.beforeloginnodechar.setForeground(QtGui.QColor(self.Style['node']))
            self.constant.beforeloginnode     = os.uname().nodename
        
        if tomake == 'user':
            self.constant.beforepromptloginchar = QtGui.QTextCharFormat()
            self.constant.beforepromptloginchar.setForeground(QtGui.QColor(self.Style['user']))
            self.constant.beforepromptlogin     = os.getlogin()
        
        if tomake == 'loc':
            self.constant.promptchar     = QtGui.QTextCharFormat()
            self.constant.promptchar.setForeground(QtGui.QColor(self.Style['loc']))
            self.constant.prompt         = os.getcwd()
            
        if tomake== 'env':
            self.constant.envchar        = QtGui.QTextCharFormat()
            self.constant.envchar.setForeground(QtGui.QColor(self.Style['env']))
            if 'VIRTUAL_ENV' in vars(os.environ):
                self.constant.env        = os.environ['VIRTUAL_ENV']

    def buildprompt(self):
        cur = self.textCursor()
        for _ in self.constant.promptMenu:
            if _ == 'env':
                if 'VIRTUAL_ENV' in vars(os.environ):
                    self.constant.env = os.environ['VIRTUAL_ENV']
                    cur.insertText('[ {0} ] '.format(self.constant.env), self.constant.envchar)
                else:
                    pass
            if _ == 'loc':
                self.constant.prompt = os.getcwd()
                cur.insertText(self.constant.prompt, self.constant.promptchar)
            if _ == 'user':
                cur.insertText(self.beforepromptlogin, self.beforepromptloginchar)
            if _ == 'node':
                cur.insertText(self.beforeloginnode, self.beforeloginnodechar)
            else:
                pass
        cur.insertText("\n❯ ")
        self.setTextCursor(cur)
            
    def lenByIter(self, lists):
        init = 0
        for i in lists:
            init += len(i)
        return init

    def keyPressEvent(self, e):
        self._stop = False
        self.cur = self.textCursor()

        if self.waitforobject:
            self._waitforobject.emit()
            self.setReadOnly(False)
            self.waitforobject = False
            self._stop = True
            
        if keyevent_to_string(e) == 'Backspace':
            self.cur.select(self.cur.BlockUnderCursor)
            if  ' ❯ ' == self.cur.selectedText():
               self._stop = True

        if keyevent_to_string(e) == 'Return':
            if self.toPlainText().split('❯ ')[-1].strip() == '': return

            if 'resultStdin' in vars(self.constant):
                if self.constant.resultStdin:
                    self.process.write(bytes(self.toPlainText()[self.land:]+'\n', 'utf8'))
                    self.land += 1
                    self.stop = True

            else:
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
            super().keyPressEvent(e)

    def keyReleaseEvent(self, e):
        pass

    def commandCheck(self, command):
        if command  == 'ls':
            cur = self.textCursor()
            self.cur.insertText('\n')
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
            if len(command.strip().split()) == 1:
                cur.insertText('\n')
                self.commandRunner_Error(bytes(str('imageShow: path doesn\'t exist'), 'utf-8'))
                self.commandRunnerFinished()
                return True
            if os.path.exists(os.path.abspath(command.strip().split()[1])):
                if os.path.isfile(os.path.abspath(command.strip().split()[1])):
                    self.hide()
                    self.parent.image.setStyleSheet(f'border-image: url("{os.path.abspath(command.strip().split()[1])}");')
                    self.parent.image.show()
                    self.parent.image.setFocus()
                    self.parent.image.hidden = False
                    
                else:
                    cur.setPosition(len(self.toPlainText()))
                    self.cur = self.textCursor()
                    self.cur.insertText('\n')
                    self.commandRunner_Error(bytes(str('imageShow: '+os.path.abspath(command.strip().split()[1]) + ' is not a file'), 'ascii'))
                    self.commandRunnerFinished()
            else:
                cur.setPosition(len(self.toPlainText()))
                cur = self.textCursor()
                cur.insertText('\n')
                self.commandRunner_Error(bytes(str('imageShow: path doesn\'t exist'), 'utf-8'))
                self.commandRunnerFinished()        
            return True

        if 'clear' == command.strip():
            self.clear()
            self.buildprompt()
            self.constant.cleared = True
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

        if 'run' == _cmd[:3] and command.strip()[3] == ' ':
            cur = self.textCursor()
            cur.insertText('\n')
            self.run(_cmd[3:].strip())
            return True
        return False

    def restorehtml(self):
        html = self.toHtml()
        self.clear()
        self.insertHtml(html)
        self.commandRunnerFinished()
        
    def run(self, cmd):
        self.process = QtCore.QProcess(self)
        self.process.readyReadStandardOutput.connect(self.PIPEstdout)
        self.process.readyReadStandardError.connect(self.PIPEstderr)
        self.process.stateChanged.connect(self.onStateChanged)
        self.process.start(cmd)
        self.land = len(self.toPlainText())
        self.constant.resultStdin = True

    def onStateChanged(self, state):
        if state == 0:
            del self.constant.resultStdin
            self.commandRunnerFinished()
        
    def message(self, s, state):
        cur = self.textCursor()
        cur.setPosition(len(self.toPlainText()))
        cur.insertText(s)
        self.land = len(self.toPlainText())
        self.setTextCursor(cur)
        self.ensureCursorVisible()

    def PIPEstderr(self):
        err    = self.process.readAllStandardError()
        stderr = bytes(err).decode('utf-8')
        self.message(stderr, 'stderr')

    def PIPEstdout(self):
        out    = self.process.readAllStandardOutput()
        stdout = bytes(out).decode('utf-8')
        self.message(stdout, 'stdout')

    def commandRunner_Error(self, e):
        cur = self.textCursor()
        char = QtGui.QTextCharFormat()
        char.setForeground(QtGui.QColor(self.Style['error']))
        cur.insertText(e.decode('utf-8'), char)
        self.setTextCursor(cur)

    def commandRunnerText(self, e):
        cur = self.textCursor()
        cur.setPosition(len(self.toPlainText()))
        try:
            self.cur.insertText(u'{0}'.format(e.decode('utf-8')))
        except Exception  as e:
            print(e)
            self.cur.insertText(str(e)[1:-1])
        self.setTextCursor(cur)
        self.ensureCursorVisible()
        
    def commandRunnerFinished(self, *args):
        self.prompt = os.getcwd() + '\n❯ '
        cur = self.textCursor()
        self.cur.insertText('\n\n'+self.prompt, self.constant.promptchar)
        self.setTextCursor(self.cur)
        self.ensureCursorVisible()
        
    def pushEditorOutput(self, e):
        pass
