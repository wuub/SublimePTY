from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor

import win32pipe
import win32console
import win32process
import win32con
import time

Coord = win32console.PyCOORDType

class ConsoleServer(object):

    def __init__(self):
        self._last_lines = {}

        win32console.FreeConsole()
        win32console.AllocConsole()
        self._con_out = win32console.GetStdHandle(win32console.STD_OUTPUT_HANDLE)
        self._con_in = win32console.GetStdHandle(win32console.STD_INPUT_HANDLE)
        flags = win32process.NORMAL_PRIORITY_CLASS
        si = win32process.STARTUPINFO()
        si.dwFlags |= win32con.STARTF_USESHOWWINDOW
        (self._handle, handle2, i1, i2) = win32process.CreateProcess(None, "cmd.exe", None, None, 0, flags, None, '.', si)

    def terminate_process(self):
        return win32process.TerminateProcess(self._handle, 0)

    def write_console_input(self, keys):
        codes = [self._input_record(key) for key in keys]
        self._con_in.WriteConsoleInput(codes)

    def _input_record(self, key):
        kc = win32console.PyINPUT_RECORDType (win32console.KEY_EVENT)
        kc.KeyDown = True
        kc.RepeatCount = 1
        cnum = ord(key)
        kc.Char = unicode(key)
        return kc

    def send_keypress(self, key, **kwds):
        self.write_console_input(key)

    def read(self):
        lines = {}
        size = self._con_out.GetConsoleScreenBufferInfo()['Window']
        for i in xrange(0, size.Bottom):
            lines[i] = self._con_out.ReadConsoleOutputCharacter(size.Right+1, Coord(0, i))
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
