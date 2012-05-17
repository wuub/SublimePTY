import win32con
import win32console
import ctypes
import winkbd

KEYMAP = {
    "enter": win32con.VK_RETURN,
    "up": win32con.VK_UP,
    "down": win32con.VK_DOWN,
    "left": win32con.VK_LEFT,
    "right": win32con.VK_RIGHT,
    "backspace": win32con.VK_BACK,
    "delete": win32con.VK_DELETE,
    "end": win32con.VK_END,
    "home": win32con.VK_HOME,
    "tab": win32con.VK_TAB,
    "f1": win32con.VK_F1,
    "f2": win32con.VK_F2,
    "f3": win32con.VK_F3,
    "f4": win32con.VK_F4,
    "f5": win32con.VK_F5,
    "f6": win32con.VK_F6,
    "f7": win32con.VK_F7,
    "f8": win32con.VK_F8,
    "f9": win32con.VK_F9,
    "f10": win32con.VK_F10,
    "f11": win32con.VK_F11,
    "f12": win32con.VK_F11,
    "pageup": win32con.VK_PRIOR,
    "pagedown": win32con.VK_NEXT,
    "escape": win32con.VK_ESCAPE
    }

CONTROL_KEY_STATE_FLAGS = {
    "ctrl": win32con.LEFT_CTRL_PRESSED,
    "shift": win32con.SHIFT_PRESSED,
    "alt": win32con.LEFT_ALT_PRESSED,
    "super": 0
}

def flag_value(flags_dict, **kwds):
    """ compute flag value for dictionary with true/false values"""
    flag = 0
    for k,v in kwds.items():
        if v:
            flag |= flags_dict[str(k)]
    return flag

def make_input_key(key, **kwds):
    kc = win32console.PyINPUT_RECORDType(win32console.KEY_EVENT)
    kc.KeyDown = True
    kc.RepeatCount = 1
    kc.ControlKeyState = flag_value(CONTROL_KEY_STATE_FLAGS, **kwds)

    if key in KEYMAP:
        kc.Char = unicode(chr(KEYMAP[key]))
        kc.VirtualKeyCode = KEYMAP[key]
    elif len(key) == 1:
        actual_char = winkbd.kb_to_unicode(key, **kwds)
        virtual_key_code, kb_states = winkbd.unichar_to_virtual_key(unicode(actual_char))
        actual_states = flag_value(CONTROL_KEY_STATE_FLAGS, **kb_states)

        kc.Char = unicode(actual_char)
        kc.VirtualKeyCode = virtual_key_code
        kc.ControlKeyState = actual_states
    else:
        raise RuntimeError("no such key %s"% (key,))
    return kc
