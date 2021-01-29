from PyQt5 import QtWidgets, QtCore, QtGui
import syntax, pynput, sys, os, subprocess

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

class WorkerSignals(QtCore.QObject):
    text     = QtCore.pyqtSignal(object)
    error    = QtCore.pyqtSignal()
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
            from subprocess import Popen, PIPE
            process = Popen(self.command, stdout=PIPE, shell=True)
            while True:
                if self.breakthebond :
                    self.signals.finished.emit()
                    break
                line = process.stdout.readline().rstrip()
                if not line:
                    self.signals.finished.emit()
                    break
                self.signals.text.emit(line)

        except Exception as e:
            print(e)
            self.signals.error.emit()

    def _break_(self):
        self.breakthebond = True

class plain(QtWidgets.QTextEdit):
    def __init__(self, parent, fore):
        super().__init__(parent)
        self.fore           = fore
        self.forechar       = QtGui.QTextCharFormat()
        self.forechar.setForeground(QtGui.QColor(self.fore))
        self.alphanum       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        self.modifiers      = 'Shift Control Alt +'
        self.prev           = 0
        self.grabbedEditor  = False
        self.waitforobject  = False
        self.prompt         = os.getcwd() + '\n❯ '
        self.cleared        = False
        self.Signals        = WorkerSignals()
        self._waitforobject = self.Signals.finished
        self._waitforobject.connect(self.restorehtml)

    def keyPressEvent(self, e):
        pass

    def keyReleaseEvent(self, e):
        try:
            _e = keyevent_to_string(e)
            if self.waitforobject:
                if _e == 'Backspace':
                    self._waitforobject.emit()

            if self.grabbedEditor and (_e == 'Control+C' or _e == 'Control+D'): self.commandRunner.signals._break.emit()
            if self.grabbedEditor : return
            self.cur   = self.textCursor()
            self.start = 0
            for i in self.toPlainText().split('\n')[:-1]:
                self.start += len(i) + 1

            if self.prev > self.start:
                if self.cleared:
                    self.cleared = False
                    self.prev = self.start
                else:
                    self.start = self.prev
            if self.prev < self.start:
                self.prev = self.start
            self.start += 2
            if self.cur.position() < self.start: return
                
            if _e in self.alphanum:
                self.insertPlainText(_e.lower())

            if (not '+' in _e) and (_e in self.modifiers): return


            if (_e == 'Minus'):
                    self.insertPlainText('-')

            if (_e == 'Equal'):
                    self.insertPlainText('=')

            if (_e == 'Backlash'):
                    self.insertPlainText('\\')

            if (_e == 'BracketLeft'):
                    self.insertPlainText(']')

            if (_e == 'BracketRight'):
                    self.insertPlainText('[')

            if (_e == 'Apostrophe'):
                    self.insertPlainText('\'')

            if (_e == 'Semicolon'):
                    self.insertPlainText(';')

            if (_e == 'Slash'):
                    self.insertPlainText('/')

            if (_e == 'Comma'):
                    self.insertPlainText(',')

            if (_e == 'Period'):
                    self.insertPlainText('.')
                        
            if ('Shift' in _e):
                if (_e.split('Shift+')[1] in self.alphanum):
                    self.insertPlainText(_e.split('Shift+')[1].upper())
                if (_e.split('Shift+')[1] == 'Exclam'):
                    self.insertPlainText('!')
                if (_e.split('Shift+')[1] == 'At'):
                    self.insertPlainText('@')
                if (_e.split('Shift+')[1] == 'Dollar'):
                    self.insertPlainText('$')    
                if (_e.split('Shift+')[1] == 'NumberSign'):
                    self.insertPlainText('#')
                if (_e.split('Shift+')[1] == 'Percent'):
                    self.insertPlainText('%')
                if (_e.split('Shift+')[1] == 'AsciiCircum'):
                    self.insertPlainText('^')
                if (_e.split('Shift+')[1] == 'Ampersand'):
                    self.insertPlainText('&')
                if (_e.split('Shift+')[1] == 'Asterisk'):
                    self.insertPlainText('*')
                if (_e.split('Shift+')[1] == 'ParenLeft'):
                    self.insertPlainText('(')
                if (_e.split('Shift+')[1] == 'ParenRight'):
                    self.insertPlainText(')')
                if (_e.split('Shift+')[1] == 'Underscore'):
                    self.insertPlainText('_')
                if (_e.split('Shift+')[1] == 'Plus'):
                    self.insertPlainText('+')
                if (_e.split('Shift+')[1] == 'Minus'):
                    self.insertPlainText('-')
                if (_e.split('Shift+')[1] == 'Equal'):
                    self.insertPlainText('=')
                if (_e.split('Shift+')[1] == 'Bar'):
                    self.insertPlainText('|')
                if (_e.split('Shift+')[1] == 'BraceRight'):
                    self.insertPlainText('}')
                if (_e.split('Shift+')[1] == 'BraceLeft'):
                    self.insertPlainText('{')
                if (_e.split('Shift+')[1] == 'QuoteDbl'):
                    self.insertPlainText('"')
                if (_e.split('Shift+')[1] == 'Colon'):
                    self.insertPlainText(':')
                if (_e.split('Shift+')[1] == 'Question'):
                    self.insertPlainText('?')
                if (_e.split('Shift+')[1] == 'Greater'):
                    self.insertPlainText('>')
                if (_e.split('Shift+')[1] == 'Less'):
                    self.insertPlainText('<')
                if (_e.split('Shift+')[1] == 'AsciiTilde'):
                    self.insertPlainText('~')
                
            if ('Space' in _e):
                self.insertPlainText(' ')

            if ('Backspace' in _e):
                import bs4
                if not self.cur.position() > self.start: return
                q = self.toHtml()
                _pos = self.cur.position()
                try:
                    i = ''
                    for _ in q.split('</span>')[:-2]:
                        i+=_
                    i+='</span>'
                    i+=q.split('</span>')[-2][:-1]
                    i+='</span>'
                    i+=q.split('</span>')[-1]
                    self.setHtml(i)
                    self.cur.setPosition(_pos)
                    self.setTextCursor(self.cur)
                    
                    
                except Exception as e:
                    i = ''
                    for _ in q.split('</p>')[:-2]:
                        i+=_
                    i+='</p>'
                    i+=q.split('</p>')[-2][:-1]
                    i+='</p>'
                    i+=q.split('</p>')[-1]
                    self.setHtml(i)
                    
                '''
                self.setPlainText(self.toPlainText()[:-1])
                self.cur.setPosition(i-1)
                self.setTextCursor(self.cur)
                '''
            if ('Left' in _e):
                self.cur.setPosition(self.cur.position() - 1)
                self.setTextCursor(self.cur)

            if ('Right' in _e):
                self.cur.setPosition(self.cur.position() + 1)
                self.setTextCursor(self.cur)

            if ('Return' in _e):
                self.grabbedEditor = True
                if self.commandCheck(self.toPlainText().split('❯ ')[-1]) : return
                self.commandrunnerThread = QtCore.QThread()
                self.commandrunner = commandRunner(self.toPlainText().split('❯ ')[-1])
                self.commandrunner.signals.error.connect(self.commandRunnerError)
                self.commandrunner.signals._break.connect(self.commandrunner._break_)
                self.commandrunner.signals.text.connect(self.commandRunnerText)
                self.commandrunner.signals.finished.connect(self.commandRunnerFinished)
                self.commandrunner.moveToThread(self.commandrunnerThread)
                self.commandrunnerThread.started.connect(self.commandrunner.run)
                self.commandrunner.signals.finished.connect(self.commandrunner.deleteLater)
                self.commandrunner.signals.finished.connect(self.commandrunnerThread.quit)
                self.commandrunnerThread.finished.connect(self.commandrunnerThread.deleteLater)
                self.commandrunnerThread.start()
                self.insertPlainText('\n')
            return
                
        except Exception as exp:
            print(exp)
            return

    def commandCheck(self, command):
        if command == 'ls':
            #old
            '''self.insertPlainText('\n')
            for e in os.listdir():
                cur = self.textCursor()
                cur.setPosition(len(self.toPlainText()))
                self.setTextCursor(cur)
                self.insertPlainText(str(e) + '\t')
            self.commandRunnerFinished()
            return True'''
            #new
            cur = self.textCursor()
            self.cur.insertText('\n', self.forechar)
            dirchar = QtGui.QTextCharFormat()
            dirchar.setForeground(QtGui.QColor('#9898fb'))
            filchar = QtGui.QTextCharFormat()
            filchar.setForeground(QtGui.QColor('#1E786E'))
            dirs, files = [],[]
            
            for e in os.listdir():
                if os.path.isdir(os.path.join(os.getcwd(), e)):
                    dirs.append(e)
                if os.path.isfile(os.path.join(os.getcwd(), e)):
                    files.append(e)

            for e in dirs:
                self.cur.insertText(e+'\t', dirchar)
            for e in files:
                self.cur.insertText(e+'\t', filchar)

            self.setTextCursor(cur)
            self.commandRunnerFinished()
            return True

        if 'imageShow' == command.strip().split()[0]:
            cur = self.textCursor()
            print(command.strip().split()[1])
            self.html = self.toHtml()
            self.clear()
            self.insertHtml('<img src='+ command.strip().split()[1] + ' width='+str(self.width())+' height='+str(self.height())+'>')
            self.waitforobject = True
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
        return False

    def restorehtml(self):
        self.clear()
        self.insertHtml(self.html)
        self.commandRunnerFinished()
        self.grabbedEdtor = False

    def commandRunnerError(self, *args):
        print(*args)

    def commandRunnerText(self, e):
        cur = self.textCursor()
        cur.setPosition(len(self.toPlainText()))
        print(u'{0}'.format(e.decode('ascii')))
        self.cur.insertText(u'{0}'.format(e.decode('ascii')) + '\n', self.forechar)
        self.setTextCursor(cur)
        self.ensureCursorVisible()
        
        
    def commandRunnerFinished(self, *args):
        cur = self.textCursor()
        self.cur.insertText('\n\n'+self.prompt, self.forechar)
        self.setTextCursor(self.cur)
        self.grabbedEditor = False
        self.ensureCursorVisible()
        
    def pushEditorOutput(self, e):
        pass

fore   = '#b7ccda'
app    = QtWidgets.QApplication([])
widget = QtWidgets.QWidget()
layout = QtWidgets.QVBoxLayout(widget)
editor = plain(widget, fore)
bar = editor.verticalScrollBar()
BAR = editor.horizontalScrollBar()
BAR.hide()
bar.hide()
#editor.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
#editor.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
layout.setContentsMargins(20, 20, 20, 20)
layout.addWidget(editor)
widget.setStyleSheet("""
    font-family:'Cascadia Code PL';
    font-weight:200;
    font-size: 13px;
    color: {fore};
    border: None;
    background-color: #0c1013;""".format_map({'fore':fore}))
widget.resize(QtCore.QSize(700, 400))

highlight = syntax.PythonHighlighter(editor.document())
widget.show()

a = os.getcwd()+'\n'+'❯ '
editor.insertPlainText(a)

app.exec()
