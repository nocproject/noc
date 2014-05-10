# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: MikroTik
## OS:     RouterOS
## Compatible: 3.14 and above
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.profiles import Profile as NOCProfile


class Profile(NOCProfile):
    name = "MikroTik.RouterOS"
    supported_schemes = [NOCProfile.TELNET, NOCProfile.SSH]
    command_submit = "\r"
    pattern_prompt = r"\[(?P<prompt>[^\]@]+@.+?)\] > "
    pattern_more = [
        ("Please press \"Enter\" to continue!", "\n"),
        (r"\[Q quit\|.+\]", " "),
        (r"\[[yY]/[nN]\]", "y")
    ]
    pattern_syntax_error = r"bad command name"
    config_volatile = [r"^#.*?$", r"^\s?"]

    def setup_script(self, script):
        """
        Starting from v3.14 we can specify console options
        during login process
        :param script:
        :return:
        """
        if (script.parent is None and
                not script.access_profile.user.endswith("+ct")):
            script.access_profile.user += "+ct"
        self.add_script_method(script, "cli_detail", self.cli_detail)

    def cli_detail(self, script, cmd, cached=False):
        """
        Parse RouterOS .... print detail output
        :param script:
        :param cmd:
        :param cached:
        :return:
        """
        if cached == True:
            return self.parse_detail(script.cli(cmd, cached=True))
        else:
            return self.parse_detail(script.cli(cmd))

    rx_p_new = re.compile("^\s*(?P<line>\d+)\s+")
    rx_key = re.compile("([0-9a-zA-Z\-]+)=")

    def parse_detail(self, s):
        """

        :param s:
        :return:
        """
        # Normalize
        ns = []
        flags = []
        for l in s.splitlines():
            if not l:
                continue
            if not flags and l.startswith("Flags:"):
                # Parse flags from line like
                # Flags: X - disabled, I - invalid, D - dynamic
                flags = [f.split("-", 1)[0].strip()
                         for f in l[6:].split(",")]
                continue
            match = self.rx_p_new.search(l)
            if match:
                # New item
                if ";;;" in l:
                    ns += [l.partition(";;;")[0].strip()]
                else:
                    ns += [l]
            elif ns:
                ns[-1] += " %s" % l.strip()
        # Parse
        f = "".join(flags)
        rx = re.compile(
            r"^\s*(?P<line>\d+)\s+"
            r"(?P<flags>[%s]+(?:\s+[%s]+)*\s+)?"
            r"(?P<rest>.+)$" % (f, f))
        r = []
        for l in ns:
            match = rx.match(l)
            if match:
                n = int(match.group("line"))
                f = match.group("flags")
                if f is None:
                    f = ""
                else:
                    f = f.replace(" ", "")
                # Parse key-valued pairs
                rest = match.group("rest")
                kvp = []
                while rest:
                    m = self.rx_key.search(rest)
                    if not m:
                        if kvp:
                            kvp[-1] += [rest]
                        break
                    if kvp:
                        kvp[-1] += [rest[:m.start()]]
                    kvp += [[m.group(1)]]
                    rest = rest[m.end():]
                # Convert key-value-pairs to dict
                d = {}
                for k, v in kvp:
                    v = v.strip()
                    if v.startswith("\"") and v.endswith("\""):
                        v = v[1:-1]
                    d[k] = v
                r += [(n, f, d)]
        return r
