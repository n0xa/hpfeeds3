from __future__ import absolute_import

import os
import socket
from .utils import get_inet_version

try:
    import queue
except ImportError:
    import Queue as queue

__all__ = [
    'Empty',
    'Queue',
]


Empty = queue.Queue


class Queue(queue.Queue, object):

    def __init__(self):
        super(Queue, self).__init__()
        if os.name == 'posix':
            self._putsocket, self._getsocket = socket.socketpair()
        else:
            server = socket.socket(get_inet_version('localhost'), socket.SOCK_STREAM)
            server.bind(('localhost', 0))
            server.listen(1)
            self._putsocket = socket.socket(get_inet_version(server.getsockname()[0]), socket.SOCK_STREAM)
            self._putsocket.connect(server.getsockname())
            self._getsocket, _ = server.accept()
            server.close()

    def fileno(self):
        return self._getsocket.fileno()

    def put(self, item, block=True):
        super(Queue, self).put(item, block)
        try:
            self._putsocket.send(b'x')
        except socket.error:
            # Socket might be closed or have issues, but put operation succeeded
            pass

    def get(self, block=True):
        if block:
            # For blocking operations, we need to wait for the signal first
            try:
                self._getsocket.recv(1)
            except socket.error:
                # Socket might be closed, fall back to normal queue behavior
                pass
        else:
            # For non-blocking operations, check if data is available
            try:
                self._getsocket.recv(1)
            except socket.error:
                # No signal available, so no data in queue
                raise queue.Empty()
        
        return super(Queue, self).get(block)
