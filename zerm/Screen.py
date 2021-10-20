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
                print('redrawing')
                win_size_px = self.size()
                width_count = 0
                qp          = QtGui.QPainter(self)
                pen = qp.pen()
                qp.setFont(QtGui.QFont('monospace'))
                
                rect        = QtCore.QRect(0, 0, self.width(), self._fontmet.boundingRect('j').height())
                
                #qp.setClipRect(rect)
                #print(self.textCursor.currentNode.i, '\n', self.textCursor.currentNode._grouped_txt)

                for i in range(self.size().height() // self._fontmet.height()):
                        i += self.slider.value()
                        try:
                                node = self.textCursor.list[i]
                                _ = ''
                                fontmet = self._fontmet.boundingRect('Â')
                                
                                for i in node._grouped_txt:
                                        #pen = QtGui.QPen(i[0].foreground())
                                        pen.setColor(i[0].foreground())
                                        qp.setPen(i[0].foreground())
                                        #print('fore', i[0].foreground().name(), 'back', i[0].background().name())
                                        #print(qp.pen().color().name(), i[0].background().name(), i[1])
                                        qp.fillRect(rect, i[0].background())
                                        qp.drawText(rect.x(), rect.y() + self._fontmet.height(), i[1])

                                        qp.drawText(rect.x(), rect.y()+self._fontmet.height(), str(width_count))
                                        #width_count += self._fontmet.boundingRect(i[1]).width()
                                        width_count += self._fontmet.horizontalAdvance(i[1])
                                        _ = i[1]
                                        
                                        rect.setX(width_count)
                                        rect.setWidth(max(self.rect().width()-width_count, 0))
                                        #rect.setHeight(self._fontmet.boundingRect('j').height())
                                        #qp.setClipRect(rect)
                                
                
                                width_count = 0
                                rect.setY(rect.y() + rect.height())
                                rect.setX(0)
                                rect.setHeight(self._fontmet.boundingRect('j').height())
                                rect.setWidth(self.rect().width())
                                qp.setClipRect(rect)

                        except IndexError:
                                break
