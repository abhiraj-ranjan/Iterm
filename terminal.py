from PyQt5 import QtCore, QtGui, QtWidgets
import pynput

class MyException(Exception): pass

class WorkerSignals(QtCore.QObject):
    text     = QtCore.pyqtSignal(object)
    error    = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal()

class commandRunner(QtCore.QObject):
    def __init__(self, command, *args, **kwargs):
        super().__init__()
        self.args = args
        self.kwargs = kwargs
        self.command = command
        self.signals = WorkerSignals()

    QtCore.pyqtSlot()
    def run(self):
        try:
            from subprocess import Popen, PIPE
            process = Popen(self.command, stdout=PIPE, shell=True)
            while True:
                line = process.stdout.readline().rstrip()
                if not line:
                    self.signals.finished.emit()
                    break
                self.signals.text.emit(line)

        except Exception as e:
            print(e)
            self.signals.error.emit()


class Worker(QtCore.QObject):
    def __init__(self, fn,*args , **kwargs):
        super().__init__()
        self.fn      = fn
        self.args    = args
        self.kwargs  = kwargs
        self.signals = WorkerSignals()
        
    #QtCore.pyqtSlot()
    def run(self):
        try:
            self.fn(*self.args, **self.kwargs)
        except Exception as e:
            print(e)
            self.signals.error.emit()

    def on_press(self, key):
        self.signals.text.emit(key)
        
class Ui_Form(object):
    def setupUi(self, Form):
        self.initializeRun()
         
        Form.setObjectName("Form")
        Form.resize(400, 300)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setContentsMargins(20, 20, 20, 20)
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

    def tried(self, json):
        try:
            self.font          = json['editor']['font']
        except KeyError:
            self.font          = 'Cascadia Code PL'
        try:
            self.font_size     = json['editor']['font-size']
        except KeyError:
            self.font_size     = '11pt'
        try:
            self.font_style    = json['editor']['font-style']
        except KeyError:
            self.font_style    = 'normal'
        try:
            self.font_weight   = json['editor']['font-weight']
        except KeyError:
            self.font_weight   = '400'
            
    def run(self, command):
        from subprocess import Popen, PIPE
        process = Popen(command, stdout=PIPE, shell=True)
        while True:
            line = process.stdout.readline().rstrip()
            if not line:
                break
            yield line
 
    def initializeRun(self, **kwargs):
        json = self.parser(parse='json')
        self.declare(json)
    
    def declare(self, json):
        import getpass, platform
        self.threadpool    = QtCore.QThreadPool()
        self.face          = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n<html><head><meta name="qrichtext" content="1" /><style type="text/css">\np, li { white-space: pre-wrap; }\n</style></head><body style=" '
        self.tried(json)
        self._styleHead    = self.face+"font-family:\'"+self.font+"\'; font-size:"+self.font_size+"; font-weight:"+self.font_weight+"; font-style:"+self.font_style+';">\n'
        self._styleBase    = '</body></html>'
        self._p            = '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">SPANCOL</p>'
        self.style         = self._styleHead + 'PARACOL' + self._styleBase
        self.identifiers   = {'addch':'#fffff', 'common':'black'}
        self.commandLinear = ''
        self.history       = list()
        self.paras         = ''
        self.span          = '<span>SPANTEXT</span>'
        self.Location      = '~'+ os.getcwd().split(getpass.getuser())[1]
        self.prompt        = getpass.getuser()+'@'+platform.node()+':' \
                                +self.Location+'$ '
        self.grabEditor    = False
        
    def integrateCn(self, command):
        import getpass, os, platform

        if command == pynput.keyboard.Key.enter:
            self.grabEditor = True
            b = self.currentp.split('<span>')

            tempvar = ''
            for i in range(len(b)-1):
                tempvar += b[i]
            tempvar = tempvar+'<span>'+b[-1].split('</span>')[-2][:-1]+'</span></p>'
            self.paras += tempvar
            
            self.commandrunnerThread = QtCore.QThread()
            self. commandrunner = commandRunner(b[-1].split('</span>')[-2][:-1].split(self.Location+'$ ')[1])
            self.commandrunner.signals.error.connect(self.commandRunnerError)
            self.commandrunner.signals.text.connect(self.commandRunnerText)
            self.commandrunner.signals.finished.connect(self.commandRunnerFinished)
            self.commandrunner.moveToThread(self.commandrunnerThread)
            self.commandrunnerThread.started.connect(self.commandrunner.run)
            self.commandrunner.signals.finished.connect(self.commandrunner.deleteLater)
            self.commandrunner.signals.finished.connect(self.commandrunnerThread.quit)
            self.commandrunnerThread.finished.connect(self.commandrunnerThread.deleteLater)
            self.commandrunnerThread.start()
            self.commandLinear = ''

        elif command == pynput.keyboard.Key.backspace:
            self.commandLinear  = self.commandLinear[:-1]
        elif command == pynput.keyboard.Key.space:
            self.commandLinear += ' '
        elif len(str(command)[1:-1]) == 1:
            self.commandLinear += str(command)[1:-1]

        if not self.grabEditor:
            spanText                = self.span.replace('SPANTEXT', self.prompt+self.commandLinear+'_')                
            self.spanUpdate(spanText)

    def getinfo(self):
        import platform
        print(platform.uname())

    def commandRunnerFinished(self):
        self.grabEditor = False
        print('finished')
        spanText                = self.span.replace('SPANTEXT', self.prompt+self.commandLinear+'_')                
        self.spanUpdate(spanText)

    def commandRunnerText(self, text):
        strText = str(text)[2:-1]
        print(strText)

    def commandRunnerError(self):
        print('command error failed')
        
    def spanUpdate(self, SpanText):
        _translate         = QtCore.QCoreApplication.translate
        self.currentp      = self._p.replace('SPANCOL', SpanText)
        returnText         = self.style.replace('PARACOL', self.paras+self.currentp)

        self.textEdit.setHtml(_translate("Form", returnText))
        
    def parser(self, parse=''):
        if parse == 'json':
            import json, os, sys
            if os.path.exists(os.path.join(os.getcwd(), 'config')):                
                with open('config', 'r') as file:
                    stylesheet = json.load(file)
                return stylesheet
            else:
                sys.stdout.write('can\'t load config file\n')

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
        self.textEdit.setStyleSheet('background:transparent')

    def setupFn(self):
        self.attachtracing()

    def attachtracing(self):
        self.workingThread = QtCore.QThread()
        self.worker = Worker(self._pynput_)
        self.worker.moveToThread(self.workingThread)
        self.worker.signals.error.connect(self.errorInChangeText)
        self.worker.signals.text.connect(self.textChanged)
        self.workingThread.started.connect(self.worker.run)
        self.workingThread.finished.connect(self.workingThread.deleteLater)
        self.workingThread.start()

    def textChanged(self, key):
        if self.grabEditor:
            return
        self.integrateCn(key)

    def errorInChangeText(self):
        print('error occured')

    def _pynput_(self):
        try:
            import pynput.keyboard as keyboard

        except ImportError:
            sys.stderr.write('pynput module import failed')
            sys.stderr.write('\ttry installing pynput')
    
        with keyboard.Listener(on_press=self.worker.on_press) as listener:
            if self.grabEditor:
                return
            try:
                listener.join()
            except MyException as e:
                print('{0} was pressed'.format(e.args[0]))

    
if __name__ == "__main__":
    import sys, os, json
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    a = ''
    if os.path.exists(os.path.join(os.getcwd(), 'config')):
        with open('config', 'r') as file:
            existsJsonFile = True
            a = json.load(file)
        try:
            bgcolor = a['editor']['bgcolor']
        except:
            bgcolor = 'rgb(0, 0, 0)'
        try:
            forecolor = a['editor']['text-color']
        except:
            forecolor = 'white'
    Form.setStyleSheet('background-color:{0};color:{1}'.format(bgcolor, forecolor))
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

