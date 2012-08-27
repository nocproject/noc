# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PipeSocket implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## NOC modules
from basesocket import Socket


class PipeSocket(Socket):
    def __init__(self, factory):
        self.s_fd = None
        self.r_fd = None
        super(PipeSocket, self).__init__(factory)

    def create_socket(self):
        self.r_fd, self.s_fd = os.pipe()
        self.set_status(r=True)
        self.update_status()

    def socket_is_ready(self):
        return self.r_fd is not None

    def fileno(self):
        return self.r_fd

    def write(self, msg):
        os.write(self.s_fd, msg)

    def close(self, flush=True):
        super(PipeSocket, self).close(flush)
        if self.s_fd:
            os.close(self.s_fd)
            self.s_fd = None
        if self.r_fd:
            os.close(self.r_fd)
            self.r_fd = None
        self.factory.unregister_socket(self)

    def handle_read(self):
        data = os.read(self.r_fd, 4096)
        self.on_read(data)

    def on_read(self, data):
        pass
