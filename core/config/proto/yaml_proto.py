# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Load config from environment
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import urlparse
import itertools
import os
## Third-party modules
import yaml
## NOC modules
from base import BaseProtocol


class YAMLProtocol(BaseProtocol):
    """
    Environment variables mapping
    URL:
        env:///<path>
    """
    INDENT = "  "

    def __init__(self, config, url):
        super(YAMLProtocol, self).__init__(config, url)
        c = urlparse.urlparse(url)
        if c.path == "/":
            self.path = ""
        else:
            self.path = c.path

    def load(self):
        if not os.path.exists(self.path):
            return
        with open(self.path) as f:
            data = yaml.load(f)
        for name in self.config:
            c = data
            parts = name.split(".")
            for n in parts[:-1]:
                if n in c and isinstance(c[n], dict):
                    c = c[n]
                else:
                    c = None
                    break
            if c and parts[-1] in c:
                self.config.set_parameter(name, c[parts[-1]])

    def dump(self):
        r = ["---"]
        current = []
        for path in self.config:
            v = self.config.get_parameter(path)
            if v is None:
                continue
            p = path.split(".")
            prefix = p[:-1]
            if prefix != current:
                # Common part
                current = [
                    x for x, y
                    in itertools.izip_longest(current, prefix)
                    if x == y
                ]
                for pp in prefix[len(current):]:
                    r += ["%s%s:" % (self.INDENT * len(current), pp)]
                    current += [pp]
            r += ["%s%s: %s" % (self.INDENT * len(current), p[-1], v)]
        r = "\n".join(r)
        if self.path:
            with open(self.path, "w") as f:
                f.write(r)
        else:
            print r
