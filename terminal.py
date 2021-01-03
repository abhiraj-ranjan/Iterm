from PyQt5 import QtCore, QtGui, QtWidgets

class MyException(Exception): pass

class WorkerSignals(QtCore.QObject):
    result   = QtCore.pyqtSignal(object)
    error    = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal()

class Worker(QtCore.QRunnable):
    def __init__(self, fn,*args , **kwargs):
        super().__init__()
        self.fn      = fn
        self.args    = args
        self.kwargs  = kwargs
        self.signals = WorkerSignals()
        
    QtCore.pyqtSlot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)  
        except:
            self.signals.error.emit()
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()
        
class Ui_Form(object):
    def setupUi(self, Form, stylesheet):
        self.initializeRun(stylesheet = stylesheet)
         
        Form.setObjectName("Form")
        Form.resize(400, 300)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.textEdit = QtWidgets.QTextEdit(Form)
        self.textEdit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textEdit.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textEdit.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.textEdit.setReadOnly(True)
        self.textEdit.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.textEdit.setObjectName("textEdit")
        self.horizontalLayout.addWidget(self.textEdit)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)
        
        self.setupFn()

    def initializeRun(self, **kwargs):
        self._StyleSheet = kwargs['stylesheet']
        self._styleHead  = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n<html><head><meta name="qrichtext" content="1" /><style type="text/css">\np, li { white-space: pre-wrap; }\n</style></head><body style=" font-family:\'Cascadia Code PL\'; font-size:11pt; font-weight:400; font-style:normal;">\n'
        'ReplaceMe</p></body></html>'
        self._p          = '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">'
        self.style       = (''.join(self._styleHead)).join(self._p)
        self.identifiers = {'addch':'#fffff', 'common':'black'}

    def integrateCn(self, command):
        self.parser(command, parse='addText')

    def parser(self, command, parse=''):
        if parser == 'addText':
            for i in self.getTextId(command):
                
            self._history.append('<span id='+self.getTextId(i)+'>'+i+'</span>')
            if (not self.style) and self.history:

    def getTextId(self, j):
        j = j.strip()
        if len(j.split()) != 1:
            returnText = dict()
            for i in j.split():
                    if i in self.identifiers:
                        returnText[i] = self.identifiers[i]
                    else :
                        returnText[i] = self.identifiers['common']
        else:
            if j in self.identifiers:
                returnText[i] = self.identifiers[i]
            else:
                returnText[i] = self.identifiers['common']
        return returnText

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.style.replace('ReplaceMe', ''
        self.textEdit.setHtml(_translate("Form", self.style.replace('ReplaceMe', '<span style=" color:#ffff00;">hey </span><span style=" color:#00aaff;">dfhfdh</span>')))
        self.textEdit.setStyleSheet('background:transparent')

    def setupFn(self):
        self.threadpool  = QtCore.QThreadPool()

    def attachtracing(self):
        worker = Worker(self._pynput)
        worker.signals.result.connect(self.changeText)
        worker.signals.error.connect(self.errorInChangeText)
        self.threadpool.start(worker)

    def _pynput(self):
        try:
            import pynput
        except ImportError:
            sys.stderr.write('pynput module import failed')
            sys.stderr.write('\ttry installing pynput')
            Form.close()
    
        with keyboard.Listener(on_press=self.on_press) as listener:
            try:
                listener.join()
            except MyException as e:
                print('{0} was pressed'.format(e.args[0]))

    def on_press(self, key):
        if key == keyboard.Key.esc:
            raise MyException(key)
    
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    Form.setStyleSheet('background-color:#fffff')
    ui = Ui_Form()
    ui.setupUi(Form, '')
    Form.show()
    sys.exit(app.exec_())

