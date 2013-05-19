#!/usr/bin/env python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Test for available processes and PTYs
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
import pty
import time


def test():
    n = 0
    while True:
        try:
            pid, f = pty.fork()
        except OSError:
            print "%d PTYs available" % n
            return
        if pid == 0:
            time.sleep(15)
            return
        else:
            n += 1

if __name__ == "__main__":
    test()
