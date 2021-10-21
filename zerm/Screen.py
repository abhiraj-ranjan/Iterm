#control the painting of widget

from PyQt5 import QtCore, QtWidgets, QtGui
import screenImpt
import sys

class screen(screenImpt.screenImpt):
        def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                self.slider = QtWidgets.QScrollBar(self)
                self.lay = QtWidgets.QVBoxLayout(self)
                self.lay.addWidget(self.slider)
                self.slider.valueChanged.connect(self.onScrollValueChanged)
                #self.slider.hide()

        def onScrollValueChanged(self, value):
                self.update()

        def resizeEvent(self, e):
                super().resizeEvent(e)
                self.update()

        def update(self):
                win_size_px = self.size()
                self._fontmet = QtGui.QFontMetrics(self.textCursor.font)
                char_width = self._fontmet.boundingRect('y').width()

                # Subtract the space a scrollbar will take from the usable width
                usable_width = (win_size_px.width() - QtWidgets.QApplication.instance().style().pixelMetric(QtWidgets.QStyle.PM_ScrollBarExtent))

                # Use integer division (rounding down in this case) to find dimensions
                cols = usable_width // char_width
                rows = win_size_px.height() // self._fontmet.height()

                _ = 1 if self.slider.value() == self.slider.maximum() else 0
                self.slider.setRange(0, 0 if rows >= self.textCursor.lineCount() else self.textCursor.lineCount()-rows)
                if _:
                        self.slider.setValue(self.slider.maximum())
                #self.onScrollValueChanged(self.slider.value())
                super().update()

                
        def paintEvent(self, e):
                width_count = 0
                qp          = QtGui.QPainter(self)
                qp.setFont(QtGui.QFont('monospace'))
                
                boundingrect = qp.boundingRect(self.rect(), 0x0001, 'yjA')
                rect        = QtCore.QRect(0, 0, self.width(), boundingrect.height())
                


                qp.setClipRect(rect)
                
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

                                        #qp.drawText(rect.x(), rect.y()+self._fontmet.height(), str('|'))
                                        width_count += charboundingrect.width()
                                        _ = i[1]
                                        
                                        rect.setX(width_count)
                                        rect.setWidth(max(self.width()-width_count, 0))
                                        qp.setClipRect(rect)

                                        print(f'{charboundingrect.height() == boundingrect.height()}')
                
                                width_count = 0
                                rect.setY(rect.y() + rect.height())
                                rect.setX(0)
                                rect.setHeight(boundingrect.height())
                                rect.setWidth(self.width())
                                qp.setClipRect(rect)

                        except IndexError:
                                break