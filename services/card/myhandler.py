# ----------------------------------------------------------------------
# 
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import hashlib

# NOC modules
from noc.core.comp import smart_bytes


class MyHandler(object):
    hash = None
    PREFIX = os.getcwd()

    def hashed(self, url):
        """
        Convert path to path?hash version
        :param path:
        :return:
        """
        u = url
        if u.startswith("/"):
            u = url[1:]
        path = os.path.join(self.PREFIX, u)
        if not os.path.exists(path):
            return "%s?%s" % (url, "00000000")
        with open(path) as f:
            hash = hashlib.sha256(smart_bytes(f.read())).hexdigest()[:8]
        return "%s?%s" % (url, hash)
