#control the text manuplation and editings

from PyQt5 import QtCore, QtGui
import screenAbstract
import collections


class textFormat:
        def __init__(self, fmt=None):
                '''Custom Text Format for handling and storing fore/back/underline data'''
                if fmt:
                        self._foreground = QtGui.QColor(fmt._foreground)
                        self._background = QtGui.QColor(fmt._background)
                        self._underline = bool(fmt._underline)
                        self._font = fmt._font
                else:
                        self._foreground = QtGui.QColor()
                        self._background = QtGui.QColor()
                        self._underline = False
                        self._font = QtGui.QFont()

        def font(self) -> QtGui.QFont:
                return self._font

        def foreground(self) -> QtGui.QColor:
                return self._foreground

        def background(self) -> QtGui.QColor:
                return self._background

        def underline(self) -> bool:
                return self._underline

        def setFont(self, font: QtGui.QFont) -> bool:
                self._font = QtGui.QFont(font)

        def setForeground(self, color: QtGui.QColor) -> None:
                #print('set Fore to ', color.name())
                self._foreground = QtGui.QColor(color)

        def setBackground(self, color: QtGui.QColor) -> None:
                #print('set Back to ', color.name())
                self._background = QtGui.QColor(color)

        def setUnderline(self, value: bool) -> None:
                self._underline = value

        def setFontStrikeOut(self, value: bool) -> None:
                # TODO: make font strikeout work in textFormat
                ...

        def __eq__(self, texFmt):
                if (self._foreground.name() == texFmt._foreground.name()) and \
		   (self._background.name() == texFmt._background.name()) and \
		   (self._underline == texFmt._underline):
                        return True
                return False


class Node:
        def __init__(self, i: int, font):
                self.i = i
                #fmt, char
                self.text = [['' , '' ]]
                self._grouped_txt = collections.deque()
                self.met = QtGui.QFontMetrics(font)

        def update(self):
                self._grouped_txt.clear()
                self._grouped_txt.append([self.text[0][0], '', 0])
                prev_fmt = self.text[0][0]
                
                for fmt, char in self.text:
                        if prev_fmt == fmt:
                                self._grouped_txt[-1][1] += char
                                self._grouped_txt[-1][2] += self.met.boundingRect(char).width()
                                
                        else:
                                self._grouped_txt.append([textFormat(fmt), char, self.met.boundingRect(char).width()])
                                prev_fmt = textFormat(fmt)


class textCursor:
        def __init__(self,
                     parent,
                     initlist: collections.deque,
                     defaultChar: textFormat,
                     font: QtGui.QFont,
                     ):

                self.parent = parent

                self.list = initlist
                self.defaultTextFormat = defaultChar
                self.currentTextFormat = textFormat(defaultChar)

                self.setFont(font)

                self.row = 1
                self.col = 1

                if not len(self.list):
                        self.insertPixmap()

                self.currentNode = self.list[-1]

        def lineCount(self) -> int:
                return len(self.list)

        def setFont(self, font):
                met = QtGui.QFontMetrics(font)
                info = QtGui.QFontInfo(font)

                if not info.fixedPitch():
                        self.font = QtGui.QFont('monospace')
                        met = QtGui.QFontMetrics(font)
                        return

                self.boundingRect = lambda char: met.boundingRect(char)
                self.CharWidth = self.boundingRect('j').width()
                self.CharHeight = self.boundingRect('j').height()

                self.font = QtGui.QFont(font)
                
        def insertNewLine(self):
                if self.currentNode.i+1 == len(self.list):
                        self.insertPixmap()
                        self.col = 1
                        self.list[-1].text[0][0] = textFormat(self.list[-2].text[-1][0])
                        self.list[-1].update()
                        
                self.currentNode = self.list[self.currentNode.i+1]                

        def insertPixmap(self):
                self.list.append(Node(len(self.list), self.font))

        def insertText(self, text):
                _ = self.currentNode.text
                if len(_) < self.col:
                        prev_fmt = textFormat(_[-1][0])

                        if self.currentNode._grouped_txt[-1][0] == self.currentTextFormat:
                                self.currentNode._grouped_txt[-1][1] += ' '*(self.col-len(_)-1)
                                self.currentNode._grouped_txt[-1][1] += text
                                self.currentNode._grouped_txt[-1][2] += QtGui.QFontMetrics(self.font).boundingRect(text).width()
                        else:
                                self.currentNode._grouped_txt.append([self.currentTextFormat, text, QtGui.QFontMetrics(self.font).boundingRect(text).width()])

                        for i in range(self.col-len(_)-1):
                                _.append([prev_fmt, ' '])
                        _.append([self.currentTextFormat, text])
                else:
                        _[self.col-1][0] = textFormat(self.currentTextFormat)
                        _[self.col-1][1] = text
                        self.currentNode.update()

                self.col+=1
                self.parent.update()


class screenImpt(screenAbstract.ScreenAbstract):
        def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.setAttribute(QtCore.Qt.WA_InputMethodEnabled, True)
                #self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent, True)

                fmt = textFormat()
                fmt.setForeground(self.colorDict.color8bit['fore'][self.graphicMode])
                fmt.setBackground(self.colorDict.color8bit['back'][self.graphicMode])
                fmt.setFont(self._font)
                
                self.textCursor = textCursor(self, collections.deque(), fmt, self._font)
                
        def parseCmd(self, cmd):
                for i in cmd:
                        _ = self.parser.feed(i)
                        if ord(i) == 7:
                                continue
                        elif isinstance(_, bool):
                                continue
                        elif isinstance(_, dict):
                                if _['func'] == 'SGR':
                                        self.parseEscPlusCodesList(_['params'])
                                elif _['func'] == 'CUB':
                                        self.parseMouseMovement(_['params'], 'CUB')
                                elif _['func'] == 'CUD':
                                        self.parseMouseMovement(_['params'], 'CUD')
                                elif _['func'] == 'CUF':
                                        self.parseMouseMovement(_['params'], 'CUF')
                                elif _['func'] == 'CUU':
                                        self.parseMouseMovement(_['params'], 'CUU')
                                
                        elif i == '\n':
                                self.textCursor.insertNewLine()
                        elif (not _) and (i.isprintable()):

                                self.textCursor.insertText(i)

        def parseEscPlusCodesList(self, list):
                list = [int(i) for i in list]
                for i in list:
                        if 0 <= i <= 9:
                                self.setGraphicMode(i)
                        elif 30 <= i <= 37:
                                self.setForeground(i)
                        elif 40 <= i <= 47:
                                self.setBackground(i)
                if len(list) == 3:
                        if list[0] == 38 and list[1] == 5 and 0 <= list[2] <= 255:
                                self.parse256color('')
                if len(list) == 5:
                        if list[0] == 38 and list[1] == 2 and all([0 <= i <= 255 for i in list[2:]]):
                                self.textCursor.currentTextFormat.setForeground(QtGui.QColor.fromRgb(*list[2:]))
                        if list[0] == 48 and list[1] == 2 and all([0 <= i <= 255 for i in list[2:]]):
                                self.textCursor.currentTextFormat.setBackground(QtGui.QColor.fromRgb(*list[2:]))
                return True

        def setGraphicMode(self, i):
                if i == 0:
                        self.resetColors('')
                elif i == 1:
                        self.setBold('')
                elif i == 2:
                        self.setDim('')
                elif i == 3:
                        self.setItalic('')
                elif i == 4:
                        self.setUnderline('')
                elif i == 5:
                        pass
                elif i == 6:
                        pass # not valid
                elif i == 7:
                        pass
                elif i == 8:
                        pass
                elif i == 9:
                        self.setStrikethrough('')

        def setStrikethrough(self, i):
                self.textCursor.currentTextFormat.setFontStrikeOut(True)
                return True

        def setUnderline(self, i):
                self.textCursor.currentTextFormat.setUnderlineColor(QtGui.QColor.fromRgb(255, 0, 255))
                self.textCursor.currentTextFormat.setUnderlineStyle(self.currentFmt.SingleUnderline)
                return True

        def setItalic(self, i):
                self.textCursor.currentTextFormat.setFontItalic(True)
                return True

        def resetColors(self, i):
                self.graphicMode = 0
                self.textCursor.currentTextFormat = textFormat(self.textCursor.defaultTextFormat)
                return True

        def setBold(self, i):
                self.graphicMode = 1
                name = self.textCursor.currentTextFormat.foreground().name()
                for i in self.colorDict.color8bit :
                        if name in self.colorDict.color8bit[i]:
                                self.textCursor.currentTextFormat.setForeground(QtGui.QColor(self.colorDict.color8bit[i][self.graphicMode]))
                                break
                return True

        def setDim(self, i):
                self.graphicMode = 2
                return True

        def parse256color(self, code):
                pass
        
        def setBackground(self, i):
                color = None
                if i == 40:
                        color = self.colorDict.color8bit['Black'][self.graphicMode]        
                elif i == 41:
                        color = self.colorDict.color8bit['Red'][self.graphicMode]
                elif i == 42:
                        color = self.colorDict.color8bit['Green'][self.graphicMode]
                elif i == 43:
                        color = self.colorDict.color8bit['Yellow'][self.graphicMode]
                elif i == 44:
                        color = self.colorDict.color8bit['Blue'][self.graphicMode]
                elif i == 45:
                        color = self.colorDict.color8bit['Magenta'][self.graphicMode]
                elif i == 46:
                        color = self.colorDict.color8bit['Cyan'][self.graphicMode]
                elif i == 47:
                        color = self.colorDict.color8bit['White'][self.graphicMode]

                if color:
                        self.textCursor.currentTextFormat.setBackground(QtGui.QColor(color))
                return True

        def setForeground(self, i):
                color = None
                
                if i == 30:
                        color = self.colorDict.color8bit['Black'][self.graphicMode]
                elif i == 31:
                        color = self.colorDict.color8bit['Red'][self.graphicMode]
                elif i == 32:
                        color = self.colorDict.color8bit['Green'][self.graphicMode]
                elif i == 33:
                        color = self.colorDict.color8bit['Yellow'][self.graphicMode]
                elif i == 34:
                        color = self.colorDict.color8bit['Blue'][self.graphicMode]
                elif i == 35:
                        color = self.colorDict.color8bit['Magenta'][self.graphicMode]
                elif i == 36:
                        color = self.colorDict.color8bit['Cyan'][self.graphicMode]
                elif i == 37:
                        color = self.colorDict.color8bit['White'][self.graphicMode]

                if color:
                        self.textCursor.currentTextFormat.setForeground(QtGui.QColor(color))
                return True

        def parseMouseMovement(self, params, func):
                if func == 'CUB':
                        self.textCursor.col = min(self.textCursor.col, int(params[0]))
                        return True

                if func == 'CUD':
                        _ = self.textCursor.col
                        if int(params[0]) >= (self.size().height() // self._fontmet.height()):
                                for i in range(len(self.textCursor.list), self.slider.value() + (self.size().height() // self._fontmet.height()) +1):
                                               self.textCursor.insertNewLine()
                                self.textCursor.currentNode = self.textCursor.list[self.slider.value() + (self.size().height() // self._fontmet.height())]
                        else:
                                for i in range(len(self.textCursor.list), int(params[0])+1):
                                               self.textCursor.insertNewLine()
                                self.textCursor.currentNode = self.textCursor.list[self.slider.value() + int(params[0])]
                        self.textCursor.col = _

                if func == 'CUF':
                        self.textCursor.col  = int(params[0])

                if func == 'CUP':
                        self.textCursor.currentNode = self.textCursor.line[self.slider.value()-1 + int(params[0])]
                        self.textCursor.col = int(params[0])

                if func == 'CUU':
                        _ = self.textCursor.col
                        if int(params[0]) <= (self.slider.value()):
                                self.textCursor.currentNode = self.textCursor.list[self.slider.value()]
                        else:
                                self.textCursor.currentNode = self.textCursor.list[self.slider.value() - int(params[0])]
                        self.textCursor.col = _
