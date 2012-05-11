from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor

import win32pipe
import win32console
import win32process
import win32con
import time

Coord = win32console.PyCOORDType
SmallRect = win32console.PySMALL_RECTType

BUFFER_WIDTH = 160
BUFFER_HEIGHT = 100

class ConsoleServer(object):

    def __init__(self):
        self._last_lines = {}

        win32console.FreeConsole()
        win32console.AllocConsole()
        self._con_out = win32console.GetStdHandle(win32console.STD_OUTPUT_HANDLE)
        self._con_in = win32console.GetStdHandle(win32console.STD_INPUT_HANDLE)

        self._con_out.SetConsoleScreenBufferSize(Coord(BUFFER_WIDTH, BUFFER_HEIGHT))

        flags = win32process.NORMAL_PRIORITY_CLASS
        si = win32process.STARTUPINFO()
        si.dwFlags |= win32con.STARTF_USESHOWWINDOW
        (self._handle, handle2, i1, i2) = win32process.CreateProcess(None, "cmd.exe", None, None, 0, flags, None, '.', si)


    def set_window_size(self, width, height):
        max_size = self._con_out.GetConsoleScreenBufferInfo()['MaximumWindowSize']
        required_width = min(max_size.X, width)
        required_height = min(max_size.Y, height)

        window_size = SmallRect()
        window_size.Right = required_width - 1
        window_size.Bottom = required_height - 1
        self._con_out.SetConsoleWindowInfo(True, window_size)

    def terminate_process(self):
        return win32process.TerminateProcess(self._handle, 0)

    def write_console_input(self, codes):
        self._con_in.WriteConsoleInput(codes)

    def _input_record(self, key ,**kwds):
        from win32_keymap import make_input_key
        return make_input_key(key, **kwds)

    def send_keypress(self, key, **kwds):
        self.write_console_input([self._input_record(key, **kwds)])


    def send_click(self, row, col, button=1, count=1):
        inputs = []

        mc = win32console.PyINPUT_RECORDType(win32console.MOUSE_EVENT)
        mc.MousePosition = Coord(col, row)
        mc.ButtonState = button #FROM_LEFT_1ST_BUTTON_PRESSED 
        inputs.append(mc)

        if count == 2:
            mc2 = win32console.PyINPUT_RECORDType(win32console.MOUSE_EVENT)
            mc2.MousePosition = Coord(col, row)
            mc2.ButtonState = button
            mc2.EventFlags = 2 #double click            
            inputs.append(mc2)

        mc3 = win32console.PyINPUT_RECORDType(win32console.MOUSE_EVENT)
        mc3.MousePosition = Coord(col, row)
        mc3.ButtonState = 0 #release
        inputs.append(mc3)

        self.write_console_input(inputs)
        

    def read(self):
        lines = {}
        size = self._con_out.GetConsoleScreenBufferInfo()['Window']
        idx = 0
        for i in range(size.Top, size.Bottom + 1):
            lines[idx] = self._con_out.ReadConsoleOutputCharacter(size.Right+1 - size.Left, Coord(size.Left, i))
            idx += 1
        diff_lines = {}
        last_keys = self._last_lines.keys()
        for k,v in lines.items():
            if k in last_keys and self._last_lines[k] == v:
                continue
            diff_lines[k] = v
        self._last_lines = lines
        return diff_lines


class ConsoleProtocol(LineReceiver):

    def __init__(self):
        self._console = ConsoleServer()

    def connectionLost(self, reason):
        print("Connection lost:", reason)

    def lineReceived(self, line):
        import json
        response = {"status": "error"}
        try:
            cmd = json.loads(line)
            response["result"] = self.handleCommand(cmd)
            response["status"] = "ok"
        except Exception, e:
            response["status"] = "error"
            response["description"] = unicode(e)
        self.sendLine(json.dumps(response))

    def handleCommand(self, cmd):
        method = getattr(self._console, cmd["command"])
        return method(*cmd["args"], **cmd["kwds"])

class ConsoleProtocolFactory(Factory):
    def buildProtocol(self, addr):
        return ConsoleProtocol()


if __name__ == "__main__":
    reactor.listenTCP(8828, ConsoleProtocolFactory())
    reactor.run()
