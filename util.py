from PyQt5 import QtCore

keymap = {}
for key, value in vars(QtCore.Qt).items():
    if isinstance(value, QtCore.Qt.Key):
        keymap[value] = key.partition('_')[2]

modmap = {
    QtCore.Qt.ControlModifier: keymap[QtCore.Qt.Key_Control],
    QtCore.Qt.AltModifier: keymap[QtCore.Qt.Key_Alt],
    QtCore.Qt.ShiftModifier: keymap[QtCore.Qt.Key_Shift],
    QtCore.Qt.MetaModifier: keymap[QtCore.Qt.Key_Meta],
    QtCore.Qt.GroupSwitchModifier: keymap[QtCore.Qt.Key_AltGr],
    QtCore.Qt.KeypadModifier: keymap[QtCore.Qt.Key_NumLock],
    }

def keyevent_to_string(event):
    sequence = []
    for modifier, text in modmap.items():
        if event.modifiers() & modifier:
            sequence.append(text)
    key = keymap.get(event.key(), event.text())
    if key not in sequence:
        sequence.append(key)
    return '+'.join(sequence)
