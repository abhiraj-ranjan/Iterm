#control the painting of widget

from PyQt5 import QtCore, QtWidgets, QtGui
import screenImpt


class screen(screenImpt.screenImpt):
        def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                self.slider = QtWidgets.QScrollBar(self)
                self.lay = QtWidgets.QVBoxLayout(self)
                self.lay.addWidget(self.slider)
                self.slider.valueChanged.connect(self.onScrollValueChanged)
                self.fontboundingrect = QtCore.QRect()  # to be updated on paintEvent 

        def onScrollValueChanged(self, value):
                self.update()

        def resizeEvent(self, e):
                super().resizeEvent(e)
                self.update()

        def update(self):
                win_size_px = self.size()
                self._fontmet = QtGui.QFontMetrics(self.textCursor.font)

                # Use integer division (rounding down in this case) to find dimensions
                rows = win_size_px.height() // self._fontmet.height()

                _ = 1 if self.slider.value() == self.slider.maximum() else 0
                self.slider.setRange(0, 0 if rows >= self.textCursor.lineCount() else self.textCursor.lineCount()-rows)
                if _:
                        self.slider.setValue(self.slider.maximum())
                super().update()

                
        def paintEvent(self, e: QtGui.QPaintEvent):
                width_count = 0
                qp          = QtGui.QPainter(self)
                qp.setFont(QtGui.QFont('monospace'))
                
                if not self.fontboundingrect:
                        self.fontboundingrect = qp.boundingRect(self.rect(), 0x0001, 'yjA')
                
                boundingrect = self.fontboundingrect
                rect        = QtCore.QRect(0, 0, self.width(), boundingrect.height())
                
                qp.setClipRect(rect)
                
                print(boundingrect.height())

                for i in range(self.height() // boundingrect.height()):
                        i += self.slider.value()
                        try:
                                node = self.textCursor.list[i]
                                _ = ''
                                
                                for i in node._grouped_txt:
                                        qp.setPen(i[0].foreground())
                                        charboundingrect = qp.boundingRect(rect, 0x0001, i[1])

                                        qp.fillRect(QtCore.QRect(rect.x(), rect.y(), charboundingrect.width(), charboundingrect.height()), i[0].background())
                                        qp.drawText(QtCore.QRect(rect.x(), rect.y(), charboundingrect.width(), charboundingrect.height()), 0x0001, i[1])

                                        width_count += charboundingrect.width()
                                        _ = i[1]
                                        
                                        rect.setX(width_count)
                                        rect.setWidth(max(self.width()-width_count, 0))
                                        qp.setClipRect(rect)

                                width_count = 0
                                
                                rect.setX(0)
                                rect.setY(rect.y() + rect.height())
                                rect.setWidth(self.width())
                                rect.setHeight(boundingrect.height())
                                
                                qp.setClipRect(rect)

                        except IndexError:
                                break