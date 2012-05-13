import json
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

UDP_IP="127.0.0.1"
RECV_UDP_PORT=8828
SEND_UDP_PORT=8829

class ConsoleClient(object):

    def __init__(self, host, port): 
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind((UDP_IP, SEND_UDP_PORT))
        self.is_running = True 

    def _request(self, cmd, *args, **kwds):
        try:
            req = zlib.compress(json.dumps({"command": cmd, "args": args, "kwds": kwds}))
            self._sock.sendto(req, (UDP_IP, RECV_UDP_PORT))
            res = self._sock.recv(2**15)
            resp = json.loads(zlib.decompress(res))
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