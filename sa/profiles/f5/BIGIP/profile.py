# ---------------------------------------------------------------------
# Vendor: f5
# OS:     BIG-IP
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "f5.BIGIP"

    pattern_prompt = rb"^(?P<user>\S+?)@(?P<part>\(.+?\))\(tmos\)# "
    pattern_more = [
        (rb"^---\(less \d+%\)---", b" "),
        (rb"^\(END\)", b"q"),
        (rb"Display all \d+ items\? \(y/n\) ", b"y"),
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
                    header = []
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
            elif in_header:
                header += [s]
            else:
                data += [s]

    def setup_script(self, script):
        self.add_script_method(script, "parse_blocks", self.parse_blocks)
