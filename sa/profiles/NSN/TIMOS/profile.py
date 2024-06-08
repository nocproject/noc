# ----------------------------------------------------------------------
# Vendor: NSN
# OS:     TIMOS
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile
from noc.core.ip import IPv6


class Profile(BaseProfile):
    name = "NSN.TIMOS"

    pattern_username = rb"[Ll]ogin: "
    pattern_password = rb"[Pp]assword: "
    pattern_prompt = rb"^\S+?#"
    pattern_more = [(rb"^Press any key to continue.*$", b" ")]
    pattern_syntax_error = rb"Error: Bad command\.|Error: Invalid parameter\."
    command_disable_pager = "environment no more"
    command_exit = "logout"
    config_volatile = [r"^# Finished.*$", r"^# Generated.*$"]
    rogue_chars = [re.compile(rb"\r\s+\r"), b"\r"]
    config_tokenizer = "indent"
    config_tokenizer_settings = {"line_comment": "#", "end_of_context": "exit", "string_quote": '"'}

    rx_port_name = re.compile(r"(\d+\/\d+\/\d+)")

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("0/1/1")
        '0/1/1'
        >>> Profile().convert_interface_name('port3/1/9, 10-Gig Ethernet, "--Description To 0/20/1"')
        '3/1/9'
        >>> Profile().convert_interface_name("port0/1/1")
        '0/1/1'
        """
        if self.rx_port_name.match(s):
            return s
        if "," in s:
            s = s.split(",", 1)[0].strip()
        if s.startswith("port"):
            s = s[4:]
        return s

    INTERFACE_TYPES = {
        "port": "physical",
        "lag-": "aggregated",
    }

    @classmethod
    def get_interface_type(cls, name):
        if cls.rx_port_name.match(name):
            return "physical"
        return cls.INTERFACE_TYPES.get(name[:4].lower())

    def get_linecard(self, interface_name):
        ifname = self.convert_interface_name(interface_name)
        return super().get_linecard(ifname)

    def ip_dec_to_hex(self, ip: str):
        """
        change IP from DEC in HEC.
        Exp:
        42.0.180.64.74.0.0.0.0.0.0.0.0.0.0.10 -> 2a00:b440:4a00:0000:0000:0000:0000:000a
        42.0.180.64 -> 2a0:b440
        """

        def number_to_hex(number: str):
            return "%02X" % int(number)

        ip = ip.split(".")
        ip_new = ""
        i = 0
        while i < len(ip):
            ip_new += f"{number_to_hex(ip[i])}{number_to_hex(ip[i+1])}:"
            i += 2
        return ip_new[:-1]

    repl_simv = ["\t", "\n", "\x03", "\x13", "\x10"]

    def ascii_to_str(self, key):
        """
        Decode symbols from ASCII to chr for IPv4 and IPv6
        """

        key = key.split(".")
        is_ipv6 = False
        if len(key) > 40:
            is_ipv6 = True
            pool = "".join([chr(int(c)) for c in key[1:-19]])
        else:
            pool = "".join([chr(int(c)) for c in key[1:-7]])
        for s in self.repl_simv:
            pool = pool.replace(s, ":")
        pool_mask = key[-1:][0]
        if is_ipv6:
            pool_ip = ".".join([c for c in key[-17:-1]])
            pool_ip = IPv6(f"{self.ip_dec_to_hex(pool_ip)}/{pool_mask}").normalized
            pool_ip = str(pool_ip).split("/", 1)[0]
            pool_ip = pool_ip.replace("::", ";;")  # :: use in separate scope, dont show in card
        else:
            pool_ip = ".".join([c for c in key[-5:-1]])
        return pool, pool_ip, pool_mask
