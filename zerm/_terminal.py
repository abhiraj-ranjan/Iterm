from shell import *
import json
from terminal.terminal import *
import terminal.syntax as syntax
from PyQt5 import QtWidgets

if __name__ == '__main__':
    with open(os.path.abspath(os.path.join(os.getcwd(), 'terminal', 'conf'))) as file:
        conf= json.load(file)

    app    = QtWidgets.QApplication([])

    widget = borderFrame(conf, app)
    layout = QtWidgets.QVBoxLayout(widget)

    layout.setContentsMargins(int(conf['margin-Left']), int(conf['margin-Top']), int(conf['margin-Right']), int(conf['margin-Bottom']))

    editor = QZerm(widget, conf)
    widget.initChild()
    layout.addWidget(editor)
    widget.resize(QtCore.QSize(int(conf['window_size'].split('x')[0]), int(conf['window_size'].split('x')[1])))

    widget.resize(700, 400)
    widget.setStyleSheet(conf['parent_Ss'])
    editor.setStyleSheet(conf['editor_Ss'])

    if conf['window_startup_mode'] == 'CUSTOM_FRAMELESS_WINDOW':
        widget._close.setStyleSheet(conf['window_closebt_styleSheet'])
        widget.tmin.setStyleSheet(conf['window_minbt_styleSheet'])
        widget.tshade.setStyleSheet(conf['window_shadebt_styleSheet'])
        widget.tmax.setStyleSheet(conf['window_maxbt_styleSheet'])

    editor.setFocus()

    high = syntax.PythonHighlighter(editor.document())
    widget.show()
    app.exec()
    
