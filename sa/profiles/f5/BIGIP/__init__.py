# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: f5
## OS:     BIG-IP
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import SSH


class Profile(noc.sa.profiles.Profile):
    name = "f5.BIGIP"
    supported_schemes = [SSH]
    pattern_username = "^([Uu]sername|[Ll]ogin):"
    pattern_prompt = r"^(?P<user>\S+?)@(?P<part>\(.+?\))\(tmos\)# "
    pattern_more = [
        (r"^---\(less \d+%\)---", " "),
        (r"^\(END\)", "q")
    ]
    command_exit = "quit"

    def parse_blocks(self, script, v):
        def clean(v):
            if v.startswith("| "):
                return v[2:]
            else:
                return v

        in_header = False
        header = []
        data = []
        for s in v.splitlines():
            s = s.strip()
            if not s:
                # End of block
                if header:
                    h = clean(header[0])
                    d = "\n".join([clean(x) for x in data])
                    yield h, d
                    hader = []
                    data = []
            elif s.startswith("----------"):
                if not in_header:
                    # Begin of header
                    in_header = True
                    header = []
                    data = []
                else:
                    # End of header
                    in_header = False
            else:
                if in_header:
                    header += [s]
                else:
                    data += [s]

    def setup_script(self, script):
        self.add_script_method(
            script, "parse_blocks", self.parse_blocks)