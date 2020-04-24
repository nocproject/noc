# ----------------------------------------------------------------------
# BaseTokenizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


class BaseTokenizer(object):
    name = None

    def __init__(self, data):
        self.data = data

    def __iter__(self):
        return iter(())
