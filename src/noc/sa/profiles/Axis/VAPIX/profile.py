# ---------------------------------------------------------------------
# Vendor: Axis
# OS:     VAPIX
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Axis.VAPIX"

    config_tokenizer = "line"
    config_tokenizer_settings = {"line_comment": "#", "rewrite": [(re.compile(r"[\.=\[\]]"), " ")]}
    config_normalizer = "VAPIXNormalizer"
    confdb_defaults = [
        ("hints", "protocols", "ntp", "mode", "client"),
        ("hints", "protocols", "ntp", "version", "3"),
    ]

    def get_list(self, script, command=None, eof_mark=None):
        if command is None:
            command = "/param.cgi?action=list"
            eof_mark = "root.Time.NTP"
        command = "/axis-cgi/admin" + command
        return script.http.get(command, eof_mark=eof_mark, cached=True, use_basic=True)

    def get_dict(self, script, command=None, eof_mark=None):
        r = {}
        v = self.get_list(script, command, eof_mark)
        for line in v.splitlines():
            if line.startswith("#"):
                continue
            key, value = line.split("=", 1)
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            r[key] = value
        return r
