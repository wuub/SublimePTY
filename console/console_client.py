import json
import telnetlib
import socket
import zlib


class RemoteError(Exception):
    def __init__(self, resp):
        super(RemoteError, self).__init__()
        self._resp = resp

    def __unicode__(self):
        return unicode(self._resp)

    def __str__(self):
        return str(self._resp)

class ConsoleClient(object):

    def __init__(self, host, port): 
        self._telnet = telnetlib.Telnet()
        self._telnet.open(host, int(port))
        self.is_running = True 

    def _request(self, cmd, *args, **kwds):
        try:
            req = json.dumps({"command": cmd, "args": args, "kwds": kwds})
            self._telnet.write(req)
            self._telnet.write("\r\n")
            resp = json.loads(self._telnet.read_until("\r\n"))
            if resp["status"] != "ok":
                raise RemoteError(resp)
            return resp["result"]
        except socket.error:
            self.is_running = False
            return None

    def __getattr__(self, name):
        """Automatically return procedure used to invokek remote methods"""
        from functools import partial
        proc = partial(self._request, name)
        setattr(self, name, proc) # cache! 
        return proc


if __name__ == "__main__":
    cli = ConsoleClient("localhost", 8828)
    raw_input()