# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: D-Link
## OS:     DxS
## Compatible:
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "DLink.DxS"
    pattern_more = "CTRL\+C.+?a A[Ll][Ll]"
    pattern_unpriveleged_prompt = r"^\S+:(3|6|user|operator)#"
    pattern_syntax_error = \
        r"(Available commands|Next possible completions|Ambiguous token):"
    command_super = "enable admin"
    pattern_prompt = r"(?P<hostname>\S+(:\S+)*)#"
    command_more = "a"
    command_exit = "logout"
    command_save_config = "save"
    config_volatile = ["^%.*?$"]
    telnet_naws = "\x00\x7f\x00\x7f"
    default_parser = "noc.cm.parsers.DLink.DxS.base.BaseDLinkParser"
    ##
    ## Version comparison
    ## Version format:
    ## <major>.<minor><sep><patch>
    ##
    rx_ver = re.compile(r"\d+")
    rx_blocked_session = re.compile(".*System locked by other session!",
                                    re.MULTILINE | re.DOTALL)

    def cmp_version(self, x, y):
        return cmp([int(z) for z in self.rx_ver.findall(x)],
            [int(z) for z in self.rx_ver.findall(y)])

    def get_interface_names(self, name):
        r = []
        if name.startswith("1/") or name.startswith("1:"):
            r += [name[2:]]
        else:
            r += ["1/%s" % name, "1:%s" % name]
        return r

    def root_interface(self, name):
        return name

    def convert_interface_name(self, s):
        """
        "D-Link DES-3200-10 R4.37.B008 Port 1 " -> "1"
        "PORT 7 ON UNIT 1" -> "7"
        Slot0/1 -> 1 # DES-1210-28/ME
        """
        su = s.upper().strip()
        if " PORT " in su:
            su = su.rsplit(" PORT ", 1)[-1].strip()
            if " ON UNIT " in su:
                l, r = [x.strip() for x in su.split(" ON UNIT ")]
                if r == "1":
                    return l
                else:
                    return "%s:%s" % (r, l)
            else:
                return su
        elif s.startswith("Slot0/"):
            return s[6:]
        else:
            return s

    cluster_member = None
    dlink_pager = False
    rx_pager = re.compile(r"^(Clipaging|CLI Paging)\s+:\s*Disabled\s*$",
        re.MULTILINE)

    def setup_session(self, script):
        # Cache "show switch" command and fetch CLI Paging from it
        match = self.rx_pager.search(script.cli("show switch", cached=True))
        if not match:
            self.dlink_pager = True
            script.logger.debug("Disabling CLI Paging...")
            script.cli("disable clipaging")

        # Parse path parameters
        if script.credentials["path"]:
            for p in script.credentials["path"].split("/"):
                if p.startswith("cluster:"):
                    self.cluster_member = p[8:].strip()
            # Switch to cluster member, if necessary
        if self.cluster_member:
            script.logger.debug("Switching to SIM member %s" % script.cluster_member)
            script.cli("reconfig member_id %s" % script.cluster_member)

    def shutdown_session(self, script):
        if self.cluster_member:
            script.cli("reconfig exit")
        if self.dlink_pager:
            script.cli("enable clipaging")

    rx_port = re.compile(r"^\s*(?P<port>\d+(/|:)?\d*)\s*"
        r"(\((?P<media_type>(C|F))\))?\s+(?P<admin_state>Enabled|Disabled)\s+"
        r"(?P<admin_speed>Auto|10M|100M|1000M|10G)/"
        r"((?P<admin_duplex>Half|Full)/)?"
        r"(?P<admin_flowctrl>Enabled|Disabled)\s+"
        r"(?P<status>LinkDown|Link\sDown|Err\-Disabled|Empty)?"
        r"((?P<speed>10M|100M|1000M|10G)/"
        r"(?P<duplex>Half|Full)/(?P<flowctrl>None|Disabled|802.3x))?\s+"
        r"(?P<addr_learning>Enabled|Disabled)\s*"
        r"((?P<trap_state>Enabled|Disabled)\s*)?"
        r"((?P<asd>\-)\s*)?"
        r"(\n\s+(?P<mdix>Auto|MDI|MDIX|\-)\s*)?"
        r"(\n\s+Desc(ription)?:\s*?(?P<desc>.*?))?$",
        re.MULTILINE)

    def parse_interface(self, s):
        match = self.rx_port.search(s)
        if match:
            port = match.group("port")
            media_type = match.group("media_type")
            descr = match.group("desc")
            if descr:
                descr = descr.strip()
            else:
                descr = ''
            obj = {
                "port": port,
                "media_type": media_type,
                "admin_state": match.group("admin_state") == "Enabled",
                "admin_speed": match.group("admin_speed"),
                "admin_duplex": match.group("admin_duplex"),
                "admin_flowctrl": match.group("admin_flowctrl"),
                "status": match.group("status") is None,
                "speed": match.group("speed"),
                "duplex": match.group("duplex"),
                "flowctrl": match.group("flowctrl"),
                "address_learning": match.group("addr_learning").strip(),
                "mdix": match.group("mdix"),
                "trap_state": match.group("trap_state"),
                "desc": descr
            }
            key = "%s-%s" % (port, media_type)
            return key, obj, s[match.end():]
        else:
            return None

    def get_ports(self, script, interface=None):
        if ((script.match_version(DES3200, version__gte="1.70.B007") \
        and script.match_version(DES3200, version__lte="3.00.B000"))
        or script.match_version(DES3200, version__gte="4.38.B000") \
        or script.match_version(DES3028, version__gte="2.90.B10") \
        or script.match_version(DGS3120, version__gte="3.00.B022") \
        or script.match_version(DGS3620, version__gte="2.50.017")) \
        and not script.match_version(DES3200, platform="DES-3200-28F"):
            objects = []
            if interface is not None:
                c = script.cli(("show ports %s description" % interface))
            else:
                c = script.cli("show ports description")
            for match in self.rx_port.finditer(c):
                objects += [{
                    "port": match.group("port"),
                    "media_type": match.group("media_type"),
                    "admin_state": match.group("admin_state") == "Enabled",
                    "admin_speed": match.group("admin_speed"),
                    "admin_duplex": match.group("admin_duplex"),
                    "admin_flowctrl": match.group("admin_flowctrl"),
                    "status": match.group("status") is None,
                    "speed": match.group("speed"),
                    "duplex": match.group("duplex"),
                    "flowctrl": match.group("flowctrl"),
                    "address_learning": match.group("addr_learning").strip(),
                    "mdix": match.group("mdix"),
                    "trap_state": match.group("trap_state"),
                    "desc": match.group("desc").strip()
                }]
        else:
            try:
                if interface is not None:
                    objects = script.cli(
                        "show ports %s description" % interface,
                        obj_parser=self.parse_interface,
                        cmd_next="n", cmd_stop="q"
                    )
                else:
                    objects = script.cli(
                        "show ports description",
                        obj_parser=self.parse_interface,
                        cmd_next="n", cmd_stop="q"
                    )
            except:
                objects = []
            # DES-3226S does not support `show ports description` command
            if objects == []:
                objects = script.cli(
                    "show ports", obj_parser=self.parse_interface,
                    cmd_next="n", cmd_stop="q")
        prev_port = None
        ports = []
        for i in objects:
            if prev_port and (prev_port == i['port']):
                if i['status'] == True:
                    k = 0
                    for j in ports:
                        if j['port'] == i['port']:
                            ports[k] = i
                            break
                        k = k + 1
            else:
                ports += [i]
            prev_port = i['port']
        return ports

    rx_vlan = re.compile(r"VID\s+:\s+(?P<vlan_id>\d+)\s+"
    r"VLAN Name\s+:\s+(?P<vlan_name>\S+)\s*\n"
    r"VLAN Type\s+:\s+(?P<vlan_type>\S+)\s*.+?"
    r"^(Current Tagged P|Tagged p)orts\s+:\s*(?P<tagged_ports>\S*?)\s*\n"
    r"^(Current Untagged P|Untagged p)orts\s*:\s*"
    r"(?P<untagged_ports>\S*?)\s*\n",
    re.IGNORECASE | re.MULTILINE | re.DOTALL)

    rx_vlan1 = re.compile(r"VID\s+:\s+(?P<vlan_id>\d+)\s+"
    r"VLAN Name\s+:\s+(?P<vlan_name>\S+)\s*\n"
    r"VLAN Type\s+:\s+(?P<vlan_type>\S+)\s*.*?"
    r"^Member Ports\s+:\s*(?P<member_ports>\S*?)\s*\n"
    r"(Static ports\s+:\s*\S+\s*\n)?"
    r"^(Current )?Untagged ports\s*:\s*(?P<untagged_ports>\S*?)\s*\n",
    re.IGNORECASE | re.MULTILINE | re.DOTALL)

    def get_vlans(self, script):
        vlans = []
        c = script.cli("show vlan")
        for match in self.rx_vlan.finditer(c):
            tagged_ports = \
                script.expand_interface_range(match.group("tagged_ports"))
            untagged_ports = \
                script.expand_interface_range(match.group("untagged_ports"))
            vlans += [{
                "vlan_id": int(match.group("vlan_id")),
                "vlan_name": match.group("vlan_name"),
                "vlan_type": match.group("vlan_type"),
                "tagged_ports": tagged_ports,
                "untagged_ports": untagged_ports
            }]
        if vlans == []:
            for match in self.rx_vlan1.finditer(c):
                tagged_ports = []
                untagged_ports = []
                member_ports = []
                if match.group("member_ports"):
                    member_ports = \
                        script.expand_interface_range(
                        match.group("member_ports"))
                if match.group("untagged_ports"):
                    untagged_ports = \
                        script.expand_interface_range(
                        match.group("untagged_ports"))
                for port in member_ports:
                    if port not in untagged_ports:
                        tagged_ports +=[port]
                vlans += [{
                    "vlan_id": int(match.group("vlan_id")),
                    "vlan_name": match.group("vlan_name"),
                    "vlan_type": match.group("vlan_type"),
                    "tagged_ports": tagged_ports,
                    "untagged_ports": untagged_ports
                }]
        return vlans
    
    def cleaned_config(self, config):
        if self.rx_blocked_session.search(config):
            raise BaseException("System locked by other session.")
        config = super(Profile, self).cleaned_config(config)
        return config


def DES3028(v):
    """
    DES-3028-series
    :param v:
    :return:
    """
    return v["platform"].startswith("DES-3028")

def DES3x2x(v):
    """
    DES-3x2x-series
    :param v:
    :return:
    """
    return (
        v["platform"].startswith("DES-3226") or \
        v["platform"].startswith("DES-3250") or \
        v["platform"].startswith("DES-3326") or \
        v["platform"].startswith("DES-3350")
    )

def DES3500(v):
    """
    DES-3500-series
    :param v:
    :return:
    """
    return v["platform"].startswith("DES-35")

def DES3200(v):
    """
    DES-3200-series
    :param v:
    :return:
    """
    return v["platform"].startswith("DES-3200")


def DGS3120(v):
    """
    DGS-3120-series
    :param v:
    :return:
    """
    return v["platform"].startswith("DGS-3120")


def DGS3400(v):
    """
    DGS-3400-series
    :param v:
    :return:
    """
    return ("DGS-3420" not in v["platform"] and
            v["platform"].startswith("DGS-34"))


def DGS3420(v):
    """
    DGS-3420-series
    :param v:
    :return:
    """
    return v["platform"].startswith("DGS-3420")


def DGS3600(v):
    """
    DGS-3600-series
    :param v:
    :return:
    """
    return ("DGS-3610" not in v["platform"] and
            "DGS-3620" not in v["platform"] and
            v["platform"].startswith("DGS-36"))


def DGS3620(v):
    """
    DGS-3620-series
    :param v:
    :return:
    """
    return v["platform"].startswith("DGS-3620")


def DxS_L2(v):
    if v["platform"].startswith("DES-1100") \
    or v["platform"].startswith("DES-12") \
    or v["platform"].startswith("DES-30") \
    or v["platform"].startswith("DES-32") \
    or v["platform"].startswith("DES-35") \
    or v["platform"].startswith("DES-3810") \
    or v["platform"].startswith("DGS-1100") \
    or v["platform"].startswith("DGS-12") \
    or v["platform"].startswith("DGS-30") \
    or v["platform"].startswith("DGS-32"):
        return True
    else:
        return False
