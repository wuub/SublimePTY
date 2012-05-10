import win32con
import win32console
import ctypes

KEYMAP = {
    "enter": win32con.VK_RETURN,
    "up": win32con.VK_UP,
    "down": win32con.VK_DOWN,
    "left": win32con.VK_LEFT,
    "right": win32con.VK_RIGHT,
    "backspace": win32con.VK_BACKSPACE,
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
    }

def make_input_key(key, **kwds):
    kc = win32console.PyINPUT_RECORDType(win32console.KEY_EVENT)
    kc.KeyDown = True
    kc.RepeatCount = 1

    if key in KEYMAP:    
        kc.Char = unicode(chr(KEYMAP[key]))
        kc.VirtualKeyCode = KEYMAP[key]
    elif len(key) == 1:
        kc.Char = unicode(key)
        kc.VirtualKeyCode = ctypes.windll.user32.VkKeyScanA(ord(key))
    else:
        raise RuntimeError("no such key %s"% (key,))
    return kc



    # kc = win32console.PyINPUT_RECORDType(win32console.KEY_EVENT)
    # kc.KeyDown = True
    # kc.RepeatCount = 1
    # cnum = ord(c)
    # if cnum == 3:
    #     pid_list = win32console.GetConsoleProcessList()
    #     win32console.GenerateConsoleCtrlEvent(win32con.CTRL_C_EVENT, 0)
    #     return 
    # else:
    #     kc.Char = unicode(c)
    #     if str(cnum) in CONQUE_WINDOWS_VK:
    #         kc.VirtualKeyCode = CONQUE_WINDOWS_VK[str(cnum)]
    #     else:
    #         kc.VirtualKeyCode = ctypes.windll.user32.VkKeyScanA(cnum)
    #         #kc.VirtualKeyCode = ctypes.windll.user32.VkKeyScanA(cnum+96)
    #         #kc.ControlKeyState = win32con.LEFT_CTRL_PRESSED

    # return kc
