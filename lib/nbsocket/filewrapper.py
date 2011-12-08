# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## FileWrapper implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import fcntl


class FileWrapper(object):
    """
    Wrap file to mimic socket behavior. Used in conjunction
    with Socket object
    """
    def __init__(self, fileno):
        self._fileno = fileno

    def fileno(self):
        return self._fileno

    def recv(self, *args):
        return os.read(self._fileno, *args)

    def send(self, *args):
        return os.write(self._fileno, *args)

    read = recv

    write = send

    def close(self):
        os.close(self._fileno)

    def setblocking(self, status):
        """
        Set blocking status

        :param status: 0 - non-blocking mode, 1 - blocking mode
        :type status: int
        """
        flags = fcntl.fcntl(self._fileno, fcntl.F_GETFL, 0)
        if status:
            flags &= (0xFFFFFFFF ^ os.O_NONBLOCK)  # Blocking mode
        else:
            flags |= os.O_NONBLOCK  # Nonblocking mode
        fcntl.fcntl(self._fileno, fcntl.F_SETFL, flags)
