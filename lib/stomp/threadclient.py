# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## STOMP Client thread
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
from threading import Thread, Lock
## NOC modules
from client import STOMPClient


class ThreadedSTOMPClient(STOMPClient):
    def __init__(self, *args, **kwargs):
        super(ThreadedSTOMPClient, self).__init__(*args, **kwargs)
        self.lock = Lock()

    def subscribe(self, *args, **kwargs):
        with self.lock:
            super(ThreadedSTOMPClient, self).subscribe(*args, **kwargs)

    def unsubscribe(self, *args, **kwargs):
        with self.lock:
            super(ThreadedSTOMPClient, self).unsubscribe(*args, **kwargs)

    def send(self, *args, **kwargs):
        with self.lock:
            super(ThreadedSTOMPClient, self).send(*args, **kwargs)
