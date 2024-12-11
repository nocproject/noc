# ---------------------------------------------------------------------
# Mikrotik.RouterOS profile
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "MikroTik.RouterOS"

    command_submit = b"\r"
    command_exit = "quit"
    pattern_prompt = rb"\[(?P<prompt>[^\]@]+@.+?)\] [^>]*> "
    pattern_more = [
        (rb'Please press "Enter" to continue!', b"\n"),
        (rb"q to abort", b"q"),
        (rb"\[Q quit\|.+\]", b" "),
        (rb"\[[yY]/[nN]\]", b"y"),
    ]
    pattern_syntax_error = rb"bad command name"
    config_volatile = [r"^#.*?$", r"^\s?"]
    default_parser = "noc.cm.parsers.MikroTik.RouterOS.base.RouterOSParser"
    rogue_chars = [b"\x1b[9999B", b"\r", b"\x00"]
    config_tokenizer = "routeros"
    config_normalizer = "RouterOSNormalizer"
    confdb_defaults = [
        ("hints", "protocols", "ntp", "mode", "server"),
        ("hints", "protocols", "ntp", "version", "3"),
    ]
    collators = ["noc.core.confdb.collator.ifname.IfNameCollator"]

    # telnet_naws = "\x00\xfa\x00\xfa"

    def setup_script(self, script):
        """
        Starting from v3.14 we can specify console options
        during login process
        :param script:
        :return:
        """
        if script.parent is None:
            user = script.credentials.get("user", "") or ""
            if not user.endswith("+ct255w255h"):
                script.credentials["user"] = user + "+ct255w255h"
        self.add_script_method(script, "cli_detail", self.cli_detail)

    def setup_session(self, script):
        # Remove duplicates prompt. Do not remove this.
        script.cli("")

    def get_interface_names(self, name):
        r = [name]
        if "/" in name:
            # Mkt/lacp1/sfp-sfpplus2
            r = [name.split("/")[-1]]
        return r

    def clean_lldp_neighbor(self, obj, neighbor):
        if "remote_port" in neighbor and neighbor["remote_port"].startswith("VLAN"):
            names = self.get_interface_names(neighbor["remote_port"])
            if names:
                neighbor["remote_port"] = names[0]
        return neighbor

    INTERFACE_TYPES = {
        "ethe": "physical",
        "wlan": "physical",
        "sfp-": "physical",
        "qsfp": "physical",
        "lo": "loopback",
        "_mgm": "management",
        "brid": "SVI",
        "vlan": "SVI",
        "ppp-": "tunnel",
        "pppo": "tunnel",
        "l2tp": "tunnel",
        "pptp": "tunnel",
        "ovpn": "tunnel",
        "sstp": "tunnel",
        "wg": "tunnel",
        "gre-": "tunnel",
        "ipip": "tunnel",
        "eoip": "tunnel",
        "bond": "aggregated",
    }

    @classmethod
    def get_interface_type(cls, name: str) -> str:
        """
        >>> Profile().get_interface_type("sfp-sfpplus1,VLANS")
        'physical'
        >>> Profile().get_interface_type("ether2,VLANS")
        'physical'
        >>> Profile().get_interface_type("ether3")
        'physical'
        >>> Profile().get_interface_type("vlan13")
        'SVI'
        """
        return cls.INTERFACE_TYPES.get(name[:4], "other")

    def cli_detail(self, script, cmd, cached=False):
        """
        Parse RouterOS .... print detail output
        :param script:
        :param cmd:
        :param cached:
        :return:
        """
        if cached:
            c = script.cli(cmd, cached=True)
            if c == "":  # Remove duplicates prompt. Do not remove this.
                c = script.cli("")
                c = script.cli(cmd)  # Already without the flag 'cached'
        else:
            c = script.cli(cmd)
            if c == "":  # Remove duplicates prompt. Do not remove this.
                c = script.cli("")
                c = script.cli(cmd)
        return self.parse_detail(c)

    rx_p_new = re.compile(r"^\s{0,1}(?P<line>\d+)\s+")
    rx_key = re.compile(r"([0-9a-zA-Z\-]+)=")

    def cleaned_input(self, s):
        # ESC[K erase from cursor to end of line
        if b"\x1b[K" in s:
            s = b""

        return s

    def parse_detail(self, s):
        """
        :param s:
        :return:
        """
        # Normalize
        ns = []
        flags = []
        for line in s.splitlines():
            if not line:
                continue
            if not flags and line.startswith("Flags:"):
                # Parse flags from line like
                # Flags: X - disabled, I - invalid, D - dynamic
                flags = [f.split("-", 1)[0].strip() for f in line[6:].split(",")]
                continue
            match = self.rx_p_new.search(line)
            if match:
                # New item
                if ";;;" in line:
                    ns += [line.partition(";;;")[0].strip()]
                else:
                    ns += [line]
            elif ns:
                ns[-1] += " %s" % line.strip()
        # Parse
        f = "".join(flags)
        # Some commands do not show flags
        if not f:
            f = "X"
        rx = re.compile(
            r"^\s{0,1}(?P<line>\d+)\s+(?P<flags>[%s]+(?:\s+[%s]+)*\s+)?(?P<rest>.+)$" % (f, f)
        )
        r = []
        for ll in ns:
            match = rx.match(ll)
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
                        kvp[-1] += [rest[: m.start()]]
                    kvp += [[m.group(1)]]
                    rest = rest[m.end() :]
                # Convert key-value-pairs to dict
                d = {}
                for k, v in kvp:
                    v = v.strip()
                    if v.startswith('"') and v.endswith('"'):
                        v = v[1:-1]
                    d[k] = v
                r += [(n, f, d)]
        return r
