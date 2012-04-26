import win32pipe
import win32console
import win32process
import time
import win32con
import codecs
import ctypes 
user32 = ctypes.windll.user32

CONQUE_WINDOWS_VK = {
    '3'  : win32con.VK_CANCEL,
    '8'  : win32con.VK_BACK,
    '9'  : win32con.VK_TAB,
    '12' : win32con.VK_CLEAR,
    '13' : win32con.VK_RETURN,
    '17' : win32con.VK_CONTROL,
    '20' : win32con.VK_CAPITAL,
    '27' : win32con.VK_ESCAPE,
    '28' : win32con.VK_CONVERT,
    '35' : win32con.VK_END,
    '36' : win32con.VK_HOME,
    '37' : win32con.VK_LEFT,
    '38' : win32con.VK_UP,
    '39' : win32con.VK_RIGHT,
    '40' : win32con.VK_DOWN,
    '45' : win32con.VK_INSERT,
    '46' : win32con.VK_DELETE,
    '47' : win32con.VK_HELP
}

def make_input_key(c, control_key_state=None):
    kc = win32console.PyINPUT_RECORDType (win32console.KEY_EVENT)
    kc.KeyDown = True
    kc.RepeatCount = 1
    cnum = ord(c)
    if cnum == 3:
        pid_list = win32console.GetConsoleProcessList()
        win32console.GenerateConsoleCtrlEvent(win32con.CTRL_C_EVENT, 0)
        return 
    else:
        kc.Char = unicode(c)
        if str(cnum) in CONQUE_WINDOWS_VK:
            kc.VirtualKeyCode = CONQUE_WINDOWS_VK[str(cnum)]
        else:
            kc.VirtualKeyCode = ctypes.windll.user32.VkKeyScanA(cnum)
            #kc.VirtualKeyCode = ctypes.windll.user32.VkKeyScanA(cnum+96)
            #kc.ControlKeyState = win32con.LEFT_CTRL_PRESSED

    return kc


#win32console.AttachConsole()
coord = win32console.PyCOORDType

con_stdout = win32console.GetStdHandle(win32console.STD_OUTPUT_HANDLE)
con_stdin = win32console.GetStdHandle(win32console.STD_INPUT_HANDLE)

flags = win32process.NORMAL_PRIORITY_CLASS
si = win32process.STARTUPINFO()
si.dwFlags |= win32con.STARTF_USESHOWWINDOW

(handle1, handle2, i1, i2) = win32process.CreateProcess(None, "cmd.exe", None, None, 0, flags, None, '.', si)
time.sleep(1)
#size = con_stdout.GetConsoleScreenBufferInfo()['Window']
# with codecs.open("log.txt", "w", "utf8") as f:
	# for i in xrange(0, size.Bottom):
		# f.write(con_stdout.ReadConsoleOutputCharacter(size.Right+1, coord(0, i)))
		# f.write("\n")


import socket 

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = "127.0.0.1"
PORT = 5554

s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(1)

(sc, scname) = s.accept()
while True:
    msg = sc.recv(1)
    if ord(msg) == 0:
        break
    keys = [make_input_key(msg)]
    if keys:
        con_stdin.WriteConsoleInput(keys)


win32process.TerminateProcess(handle1, 0)