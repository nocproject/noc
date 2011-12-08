# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PopenSocket implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import subprocess
## NOC modules
from noc.lib.nbsocket.basesocket import Socket
from noc.lib.nbsocket.filewrapper import FileWrapper


class PopenSocket(Socket):
    """
    Wrap popen() call to mimic socket behavior
    """
    def __init__(self, factory, argv):
        super(PopenSocket, self).__init__(factory)
        self.argv = argv
        self.update_status()

    def create_socket(self):
        self.debug("Launching %s" % self.argv)
        self.p = subprocess.Popen(self.argv, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        self.socket = FileWrapper(self.p.stdout.fileno())

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

    def close(self, flush=False):
        Socket.close(self)
