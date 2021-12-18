#control the abstraction and backend of screen

from PyQt5 import QtWidgets, QtCore, QtGui
import fcntl, locale, pty, struct, termios
import subprocess
import os
from parser import parser
import colorDict


class ScreenAbstract(QtWidgets.QWidget):
        aboutToClose = QtCore.pyqtSignal()
        
        def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.config()
                
                target_width = (self._fontmet.boundingRect(self.ref_ch * self._default_cols).width() +
                                QtWidgets.QApplication.instance().style().pixelMetric(QtWidgets.QStyle.PM_ScrollBarExtent))

                self.resize(target_width, self._fontmet.height() * self._default_rows)

                # Launch DEFAULT_TTY_CMD in the terminal
                self.spawn(self._def_term)
                self.parser = parser.TempParser()

        def config(self):
                self._font           = QtGui.QFont('Cascadia Code PL', 10)
                self._fontmet        = QtGui.QFontMetrics(self._font)
                self.textChar        = QtGui.QTextCharFormat()
                self.graphicMode     = 0
                self.defaultFmt      = QtGui.QTextCharFormat()
                
                self.textChar.setFont(self._font)
                self.defaultFmt.setFont(self._font)

                self.colorDict = colorDict

                fore = QtGui.QColor(colorDict.color8bit['fore'][0])
                back = QtGui.QColor(colorDict.color8bit['back'][0])

                self.defaultFmt.setForeground(fore)
                self.defaultFmt.setBackground(back)

                self.textChar.setForeground(fore)
                self.textChar.setBackground(back)

                self.setStyleSheet(f'background: {colorDict.color8bit["back"][0]}')

                ## PTY

                # Do due diligence to figure out what character coding child
                # applications will expect to speak
                self.codec = locale.getpreferredencoding()
                self.pty_m = None
                self.notifier = None
                self.subproc = None
                self.ref_ch = 'j'
                self._default_cols = 80
                self._default_rows = 25
                self._def_term = ['bash']

        def termsize(self):
                #char_width = self.fontboundingrect.width() if self.fontboundingrect else self._fontmet.boundingRect(self.ref_ch).width()
                char_width = self._fontmet.averageCharWidth()

                cols = self.width() // char_width
                rows = self.height() // (self.fontboundingrect.height() if self.fontboundingrect else self._fontmet.boundingRect(self.ref_ch).height())

                return (cols, rows)

        def resizeEvent(self, event):
                """Handler to announce terminal size changes to child processes"""
                # Call Qt's built-in resize event handler
                super().resizeEvent(event)

                cols, rows = self.termsize()
                # Announce the change to the PTY
                fcntl.ioctl(self.pty_m, termios.TIOCSWINSZ,
                        struct.pack("HHHH", rows, cols, 0, 0))

        def spawn(self, argv):
                """Launch a child process in the terminal"""
                # Clean up after any previous spawn() runs
                # TODO: Need to reap zombie children
                # XXX: Kill existing children if spawn is called a second time?
                if self.pty_m:
                        self.pty_m.close()
                if self.notifier:
                        self.notifier.disconnect()

                # Create a new PTY with both ends open
                self.pty_m, pty_s = pty.openpty()

                # Stop the PTY from echoing back what we type on this end

                #term_attrs = termios.tcgetattr(pty_s)
                #term_attrs[3] &= ~termios.ECHO
                #termios.tcsetattr(pty_s, termios.TCSANOW, term_attrs)

                child_env = os.environ.copy()

                # Launch the subprocess
                # FIXME: Keep a reference so we can reap zombie processes
                subprocess.Popen(argv,  # nosec
                        stdin=pty_s, stdout=pty_s, stderr=pty_s,
                        env=child_env,
                        preexec_fn=os.setsid)

                # Close the child side of the PTY so that we can detect when to exit
                os.close(pty_s)

                # Hook up an event handler for data waiting on the PTY
                # (Because I didn't feel like looking into whether QProcess can be
                #  integrated with PTYs as a subprocess.Popen alternative)
                self.notifier = QtCore.QSocketNotifier(
                        self.pty_m, QtCore.QSocketNotifier.Read, self)
                self.notifier.activated.connect(self.parseData)

        def parseData(self, pty_m):
                try:
                        # Use 'replace' as a not-ideal-but-better-than-nothing way to deal
                        # with bytes that aren't valid in the chosen encoding.
                        child_output = os.read(self.pty_m, 1024).decode(
                        self.codec, 'replace')
                except OSError:
                        # Ask the event loop to exit and then return to it
                        self.close()
                        return

                self.parseCmd(child_output)

        def keyPressEvent(self, e):
                os.write(self.pty_m, e.text().encode(self.codec))

        def close(self):
                self.aboutToClose.emit()
                super().close()
