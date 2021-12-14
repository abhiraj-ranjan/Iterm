class Ansi:
        def __init__(self):
                self.funclist = {
                        'SCI' : self._SCI,
                        'OSC' : False,
                        'LineSize': self.lineSize,
                        }

                self.matchlist = {i:False for i in self.funclist}

                self.tempvar = ['']
                
        def active(self):
                return next(filter(lambda x: self.matchlist[x], self.matchlist), '')

        def resetAtty(self):
                self.tempvar = ['']
                self.toggleActive()

        def toggleActive(self):
                _ = self.active()
                if not _:
                        return
                self.matchlist[_] = False

        def lineSize(self, char):
                if char == '3':
                        self.resetAtty()
                        return {
                                'func':'LineSize#3',
                                'help':'Change this line to double-height top half',
                                }
                if char == '4':
                        self.resetAtty()
                        return {
                                'func':'LineSize#4',
                                'help':'Change this line to double-height bottom half',
                                }
                if char == '5':
                        self.resetAtty()
                        return {
                                'func':'LineSize#5',
                                'help':'Change this line to single-width single-height',
                                }
                if char == '6':
                        self.resetAtty()
                        return {
                                'func':'LineSize#6',
                                'help':'Change this line to double-width single-height',
                                }

        def _SCI(self, char):
                if char == 'R':
                        _ = self.tempvar
                        self.resetAtty()
                        return {
                                'func'  :'CPR',
                                'params': list(map(lambda x: 1 if x=='' else x, _)),
                                'help'  :'The CPR sequence reports the active position by means of the parameters.'
                                        'This sequence has two parameter values,'
                                        'the first specifying the line and the second specifying the column.'
                                        'The default condition with no parameters present, or parameters of 0, is equivalent'
                                        'to a cursor at home position.'
                                }
                if char == 'D':
                        _ = self.tempvar
                        self.resetAtty()
                        return {
                                'func'  :'CUB',
                                'params': list(map(lambda x: 1 if x in ('', 0) else x, _)),
                                'help'  :'The CUB sequence moves the active position to the left.'
                                        'The distance moved is determined by the parameter.'
                                        'If the parameter value is zero or one, the active position is moved one position to the left.'
                                        'If the parameter value is n, the active position is moved n positions to the left.'
                                        'If an attempt is made to move the cursor to the left of the left margin,'
                                        'the cursor stops at the left margin'
                                }
                if char == 'B':
                        _  = self.tempvar
                        self.resetAtty()
                        return {
                                'func'  :'CUD',
                                'params': list(map(lambda x: 1 if x in ('', 0) else x, _)),
                                'help'  :'The CUD sequence moves the active position downward without '
                                        'altering the column position. The number of lines moved is determined by the parameter.'
                                        'If the parameter value is zero or one, the active position is moved one line downward.'
                                        'If the parameter value is n, the active position is moved n lines downward.'
                                        'In an attempt is made to move the cursor below the bottom margin,'
                                        'the cursor stops at the bottom margin.'
                                }
                if char == 'C':
                        _  = self.tempvar
                        self.resetAtty()
                        return {
                                'func'  :'CUF',
                                'params': list(map(lambda x: 1 if x in ('', 0) else x, _)),
                                'help'  :'The CUF sequence moves the active position to the right.'
                                        'The distance moved is determined by the parameter.'
                                        'A parameter value of zero or one moves the active position one position to the right.'
                                        'A parameter value of n moves the active position n positions to the right.'
                                        'If an attempt is made to move the cursor to the right of the right margin, '
                                        'the cursor stops at the right margin'
                                }
                if char == 'H':
                        _  = self.tempvar
                        self.resetAtty()
                        return {
                                'func'  :'CUP',
                                'params': list(map(lambda x: 1 if x in ('', 0) else x, _)),
                                'help'  :'The CUP sequence moves the active position to the position specified by the parameters.'
                                        'This sequence has two parameter values, the first specifying the line position '
                                        'and the second specifying the column position. A parameter value of zero or one '
                                        'for the first or second parameter moves the active position to the first line or'
                                        'column in the display, respectively. The default condition with no parameters '
                                        'present is equivalent to a cursor to home action. In the VT100, this control behaves'
                                        'identically with its format effector counterpart, HVP'
                                }
                if char == 'A':
                        _  = self.tempvar
                        self.resetAtty()
                        return {
                                'func'  :'CUU',
                                'params': list(map(lambda x: 1 if x in ('', 0) else x, _)),
                                'help'  :'Moves the active position upward without altering the column position.'
                                        'The number of lines moved is determined by the parameter.'
                                        'A parameter value of zero or one moves the active position one line upward.'
                                        'A parameter value of n moves the active position n lines upward.'
                                        'If an attempt is made to move the cursor above the top margin,'
                                        'the cursor stops at the top margin.'
                                }

                # DA – Device Attributes

                # DSR – Device Status Report

                # ED
                if char == 'J':
                        _  = self.tempvar
                        self.resetAtty()
                        return {
                                'func'  :'ED',
                                'params': list(map(lambda x: 0 if x in ('', 0) else x, _)),
                                'help'  :'This sequence erases some or all of the characters in the display'
                                        ' according to the parameter. Any complete line erased by this '
                                        'sequence will return that line to single width mode\n'
                                        '0 - From cursor to end of the screen\n'
                                        '1 - From beginning of screen to cursor\n'
                                        '2 - Entire Screen'
                                }

                if char == 'K':
                        _  = self.tempvar
                        self.resetAtty()
                        return {
                                'func'  :'EL',
                                'params': list(map(lambda x: 0 if x in ('', 0) else x, _)),
                                'help'  :'Erases some or all characters in the active line according to the parameter\n'
                                        'Parameter 	Parameter Meaning\n'
                                        '0      	Erase from the active position to the end of the line, inclusive (default)\n'
                                        '1      	Erase from the start of the screen to the active position, inclusive\n'
                                        '2      	Erase all of the line, inclusive'
                                }

                if char == 'f':
                        _  = self.tempvar
                        self.resetAtty()
                        return {
                                'func'  :'HVP',
                                'params': list(map(lambda x: 1 if x in ('', 0) else x, _)),
                                'help'  :'Moves the active position to the position specified by the parameters.\n'
                                        'This sequence has two parameter values, the first specifying the line position'
                                        'and the second specifying the column. A parameter value of either zero or one'
                                        'causes the active position to move to the first line or column in the display,'
                                        'respectively. The default condition with no parameters present moves the active'
                                        'position to the home position. In the VT100, this control behaves identically with'
                                        'its editor function counterpart, CUP. The numbering of lines and columns depends'
                                        'on the reset or set state of the origin mode (DECOM).'
                                }
                if char == 'l':
                        _  = self.tempvar
                        self.resetAtty()
                        return {
                                'func'  :'RM',
                                'params': _,
                                'help'  :'Resets one or more VT100 modes as specified by each selective parameter'
                                        'in the parameter string. Each mode to be reset is specified by a separate parameter.'
                                }

                # SGR
                if char =='m':
                        _  = self.tempvar
                        self.resetAtty()
                        return {
                                'func'  :'SGR',
                                'params': list(map(lambda x: 0 if x in ('', 0) else x, _)),
                                'help'  :'Invoke the graphic rendition specified by the parameter(s). All following characters'
                                        'transmitted to the VT100 are rendered according to the parameter(s) until the next'
                                        'occurrence of SGR. \n'

                                        'Parameter 	Parameter Meaning\n'
                                        '0       	Attributes off\n'
                                        '1      	Bold or increased intensity\n'
                                        '4      	Underscore\n'
                                        '5      	Blink\n'
                                        '7      	Negative (reverse) image\n'

                                        'All other parameter values are ignored.'

                                        'With the Advanced Video Option, only one type of character attribute is possible'
                                        'as determined by the cursor selection; in that case specifying either the underscore'
                                        'or the reverse attribute will activate the currently selected attribute. ',
                                }
                if char == 'h':
                        _  = self.tempvar
                        self.resetAtty()
                        return {
                                'func'  : 'SM',
                                'params': _,
                                'help'  :'Causes one or more modes to be set within the VT100 as specified by each selective '
                                        'parameter in the parameter string. Each mode to be set is specified by a separate parameter.'
                                        'A mode is considered set until it is reset by a reset mode (RM) control sequence.'
                                }
                if char == 'r':
                        _  = self.tempvar
                        self.resetAtty()
                        return {
                                'func'  : 'ScrollingRegion',
                                'params': _,
                                'help'  :'Pt is the number of the top line of the scrolling region; '
                                'Pb is the number of the bottom line of the scrolling region and must be greater than Pt.',
                                }
                if char == 'g':
                        _  = self.tempvar
                        self.resetAtty()
                        return {
                                'func'  : 'ClearTabs',
                                'params': list(map(lambda x: 0 if x in ('', 0) else x, _)),
                                'help'  :'0 - clear tab at current column'
                                        '3 - Clear all tabs',
                                }
                

                if isinstance(self.tempvar, list) :
                        if char == ';':
                                self.tempvar.append('')
                                return True
                        else:
                                self.tempvar[-1] += char
                                return True


        def feed(self, char):
                _ = self.active()
                if _:
                        return self.funclist.get(_)(char)
                if char == '[':
                        self.matchlist['SCI'] = True

                if char == '#':
                        self.matchlist['LineSize'] = True

                if char == 'H':
                        return {
                                'func':'HTS',
                                'help':'Set one horizontal stop at the active position.'
                                }

                if char == 'D':
                        return {
                                'func':'IND',
                                'help':'This sequence causes the active position to move downward'
                                        'one line without changing the column position.\n'
                                        'If the active position is at the bottom margin, a scroll up is performed.'
                                }
                if char == 'E':
                        return {
                                'func':'NEL',
                                'help':'This sequence causes the active position to move to the first'
                                        'position on the next line downward. If the active position is at the'
                                        'bottom margin, a scroll up is performed.'
                                }
                if char == 'M':
                        return {
                                'func':'RI',
                                'help':'Move the active position to the same horizontal position on the preceding line.'
                                        'If the active position is at the top margin, a scroll down is performed'
                                }
                if char == 'c':
                        return {
                                'func':'RIS',
                                'help':'Reset the VT100 to its initial state, i.e., the state it has after it is powered on.'
                                        'This also causes the execution of the power-up self-test and signal '
                                        'INIT H to be asserted briefly.'
                                }
                if char == 'A':
                        return {
                                'func':'Cursor UP',
                                'help':'Move the active position upward one position without altering the'
                                        ' horizontal position. If an attempt is made to move the cursor'
                                        'above the top margin, the cursor stops at the top margin.'
                                }
                if char == 'B':
                        return {
                                'func':'Cursor DOWN',
                                'help':'Move the active position downward one position without altering the'
                                ' horizontal position. If an attempt is made to move the cursor below the'
                                ' bottom margin, the cursor stops at the bottom margin.'
                                }
                if char == 'C':
                        return {
                                'func':'Cursor RIGHT',
                                'help':'Move the active position to the right. If an attempt is made to move'
                                        ' the cursor to the right of the right margin, the cursor stops at the right margin.'
                                }
                if char == 'D':
                        return {
                                'func':'Cursor LEFT',
                                'help':'Move the active position one position to the left. If an attempt is '
                                        'made to move the cursor to the left of the left margin, the cursor stops at the left margin.'
                                }
                if char == 'H':
                        return {
                                'func':'Cursor HOME',
                                'help':'Move the cursor to the home position.'
                                }
                if char == 'I':
                        return {
                                'func':'Reverse Line Feed',
                                'help':'Move the active position upward one position without altering the column position. '
                                        'If the active position is at the top margin, a scroll down is performed.'
                                }
                if char == 'J':
                        return {
                                'func':'Erase to End Of Screen',
                                'help':'Erase all characters from the active position to the end of the screen.'
                                        'The active position is not changed.'
                                }
                if char == 'K':
                        return {
                                'func':'Erase to End Of Line',
                                'help':'Erase all characters from the active position to the end of the current line.'
                                        'The active position is not changed.'
                                }


class TempParser:
        def __init__(self):
                self.ansi = False
                self.AnsiParser = Ansi()

        def feed(self, char):
                if char == '\x1b':
                        self.ansi = True
                        return True
                
                if self.ansi:
                        _ = self.AnsiParser.feed(char)
                        if _:
                                if isinstance(_, bool):
                                        return _
                                if isinstance(_, dict):
                                        self.ansi = False
                                        return _
                        else:
                                if not self.AnsiParser.active():
                                        self.ansi = False
                                        return
                                return True


'''import subprocess
_ = subprocess.getoutput('screenfetch')
parser = TempParser()
for i in _:
        #print(i, end='')
        _ = parser.feed(i)
        if not _:
                pass
                print(i, end='')
        else:
                if isinstance(_, bool):
                        pass
                else:
                        _.pop('help')
                        print('\n', _)
'''
