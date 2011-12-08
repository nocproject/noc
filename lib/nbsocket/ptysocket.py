# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PTYSocket implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import pty
import signal
## NOC modules
from noc.lib.nbsocket.basesocket import Socket
from noc.lib.nbsocket.filewrapper import FileWrapper


class PTYSocket(Socket):
    """
    Wrap PTY to mimic socket behavior
    """
    def __init__(self, factory, argv):
        self.pid = None
        self.argv = argv
        self.out_buffer = ""
        super(PTYSocket, self).__init__(factory)

    def create_socket(self):
        self.debug("EXECV(%s)" % str(self.argv))
        try:
            self.pid, fd = pty.fork()
        except OSError:
            self.debug("Cannot get PTY. Closing")
            self.close()
            return
        if not self.pid:
            os.execv(self.argv[0], self.argv)
        else:
            self.socket = FileWrapper(fd)
            super(PTYSocket, self).create_socket()

    def handle_read(self):
        try:
            data = self.socket.read(self.READ_CHUNK)
        except OSError:
            self.close()
            return
        self.update_status()
        if data:
            self.on_read(data)
        else:
            self.close()

    def can_write(self):
        return bool(self.out_buffer)

    def handle_write(self):
        sent = self.socket.send(self.out_buffer)
        self.out_buffer = self.out_buffer[sent:]

    def handle_connect(self):
        self.is_connected = True
        self.on_connect()

    def write(self, msg):
        self.debug("write(%s)" % repr(msg))
        self.out_buffer += msg

    def close(self, flush=False):
        Socket.close(self)
        if self.pid is None:
            return
        try:
            pid, status = os.waitpid(self.pid, os.WNOHANG)
        except OSError:
            return
        if pid:
            self.debug("Child pid=%d is already terminated. Zombie released" % pid)
        else:
            self.debug("Child pid=%d is not terminated. Killing" % self.pid)
            try:
                os.kill(self.pid, signal.SIGKILL)
            except:
                self.debug("Child pid=%d was killed from another place" % self.pid)

    def on_read(self, data):
        pass
