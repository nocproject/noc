# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Load config from YAML
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function, absolute_import
import itertools
import os
import six
# Third-party modules
import yaml
# NOC modules
from .base import BaseProtocol


class YAMLProtocol(BaseProtocol):
    """
    Environment variables mapping
    URL:
        yaml:///<path>
    """
    INDENT = "  "
    ESCAPE_START = ("@", "%", "&")

    def __init__(self, config, url):
        super(YAMLProtocol, self).__init__(config, url)
        if self.parsed_url.path == "/":
            self.path = ""
        else:
            self.path = self.parsed_url.path

    def load(self):
        if not os.path.exists(self.path):
            return
        with open(self.path) as f:
            data = yaml.load(f)
        if data:
            self.config.update(data)

    def dump(self):
        r = ["---"]
        current = []
        for path in self.config:
            v = self.config.dump_parameter(path)
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
            if isinstance(v, six.string_types) and v.startswith(self.ESCAPE_START):
                v = "\\" + v
            r += ["%s%s: %s" % (self.INDENT * len(current), p[-1], v)]
        r = "\n".join(r)
        if self.path:
            with open(self.path, "w") as f:
                f.write(r)
        else:
            print(yaml.dump(yaml.load(r), default_flow_style=False))
