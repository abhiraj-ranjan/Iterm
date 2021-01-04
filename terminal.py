from PyQt5 import QtCore, QtGui, QtWidgets
import pynput

class MyException(Exception): pass

class WorkerSignals(QtCore.QObject):
    text     = QtCore.pyqtSignal(object)
    error    = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal()

class Worker(QtCore.QRunnable):
    def __init__(self,*args , **kwargs):
        super().__init__()
        self.args    = args
        self.kwargs  = kwargs
        self.signals = WorkerSignals()
        
    QtCore.pyqtSlot()
    def run(self):
        try:
            import pynput.keyboard as keyboard

        except ImportError:
            sys.stderr.write('pynput module import failed')
            sys.stderr.write('\ttry installing pynput')
            
        with keyboard.Listener(on_press=self.on_press) as listener:
            try:
                listener.join()
            except MyException as e:
                print('{0} was pressed'.format(e.args[0]))

    def on_press(self, key):
        self.signals.text.emit(key)
        #if key == keyboard.Key.esc:
        #    raise MyException(key)
        
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
             

    def initializeRun(self, **kwargs):
        json = self.parser(kwargs['stylesheet'], parse='json')
        self.declare(json)
    
    def declare(self, json):
        self.face          = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n<html><head><meta name="qrichtext" content="1" /><style type="text/css">\np, li { white-space: pre-wrap; }\n</style></head><body style=" '
        self.tried(json)
        self._styleHead    = self.face+"font-family:\'"+self.font+"\'; font-size:"+self.font_size+"; font-weight:"+self.font_weight+"; font-style:"+self.font_style+';">\n'
        self._styleBase    = '</p></body></html>'
        self._p            = '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">'
        self.style         = self._styleHead + self._p + 'ReplaceBySPAN' + self._styleBase
        self.identifiers   = {'addch':'#fffff', 'common':'black'}
        self.commandLinear = ''
        self.history       = list() 
        self.span          = '<span>SPANTEXT</span>'
        
    def integrateCn(self, command):
        import getpass, os, platform

        if   command == pynput.keyboard.Key.enter:
            self.history.append(self._p)
        elif command == pynput.keyboard.Key.backspace:
            self.commandLinear  = self.commandLinear[:-1]
        elif command == pynput.keyboard.Key.space:
            self.commandLinear += ' ' 
        elif len(str(command)[1:-1]) == 1:
            self.commandLinear += str(command)[1:-1]
            
        spanHeaders             = getpass.getuser()+'@'+platform.node()+':' \
                                +'~'+ os.getcwd().split(getpass.getuser())[1]+'$ '
        spanText                = self.span.replace('SPANTEXT', spanHeaders+self.commandLinear+'_')
            
        self.spanUpdate(spanText)

    def getinfo(self):
        import platform
        print(platform.uname())
        
    def spanUpdate(self, SpanText):
        _translate         = QtCore.QCoreApplication.translate
        returnText         = self.style.replace('ReplaceBySPAN', SpanText)

        self.textEdit.setHtml(_translate("Form", returnText))
        
    def parser(self, command, parse=''):
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
        self.threadpool  = QtCore.QThreadPool()
        self.attachtracing()

    def attachtracing(self):
        worker = Worker()
        worker.signals.error.connect(self.errorInChangeText)
        worker.signals.text.connect(self.textChanged)
        self.threadpool.start(worker)

    def textChanged(self, key):
        self.integrateCn(key)

    def errorInChangeText(self):
        print('error occured')
        
    
if __name__ == "__main__":
    import sys, os, json
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    if os.path.exists(os.path.join(os.getcwd(), 'config')):
        with open('config', 'r') as file:
            a = json.load(file)
        try:
            bgcolor = a['editor']['bgcolor']
        except:
            bgcolor = 'rgb(0, 0, 0)'
    Form.setStyleSheet('background-color:{0};color:white'.format(bgcolor))
    ui = Ui_Form()
    ui.setupUi(Form, '')
    Form.show()
    sys.exit(app.exec_())

