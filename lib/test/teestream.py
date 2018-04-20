# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## stdout/stderr output collector
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import StringIO


class TeeStream(object):
    """
    stdout/stderr output collector
    """
    def __init__(self, orig):
        self.orig = orig
        self.out = StringIO.StringIO()

    def write(self, s):
        self.orig.write(s)
        self.out.write(s)

    def get(self):
        return self.out.getvalue()
