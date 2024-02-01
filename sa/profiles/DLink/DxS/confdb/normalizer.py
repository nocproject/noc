# ----------------------------------------------------------------------
# DLink.DxS config normalizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.confdb.normalizer.base import BaseNormalizer, match, ANY, REST
from noc.core.confdb.syntax.patterns import IP_ADDRESS, INTEGER
from noc.core.validators import is_int


def iter_ports(port_list):
    port_list = port_list.replace("/", ":")

    raw_port_ranges = port_list.split(",")
    port_ranges = []
    for r in raw_port_ranges:
        if "-" in r:
            ports = r.split("-")
        else:
            ports = (r, r)

        port_ranges.append(ports)

    for r in port_ranges:
        first = r[0]
        last = r[1]

        slot_num = None
        if not is_int(first):
            slot_num = first.split(":")[0]

        if slot_num:
            first = first.replace(f"{slot_num}:", "")
            last = last.replace(f"{slot_num}:", "")

        first = int(first)
        last = int(last)

        for port_num in range(first, last + 1):
            if slot_num:
                yield "%s:%s" % (slot_num, port_num)
            else:
                yield "%s" % port_num


def get_medium_type(tokens):
    for i, t in enumerate(tokens):
        if t == "auto_speed_downgrade":
            return "c"
        if t == "medium_type":
            if tokens[i + 1] == "fiber":
                return "f"
            elif tokens[i + 1] == "copper":
                return "c"
    return ""


class DLinkDxSNormalizer(BaseNormalizer):
    @match("config", "command_prompt", ANY)
    def normalize_hostname(self, tokens):
        yield self.make_hostname(tokens[2])
        yield self.make_prompt(tokens[2])

    @match("config", "ports", REST)
    def normalize_interface(self, tokens):
        # config ports 1:1-1:5,1:8 medium_type copper speed auto
        # capability_advertised  10_half 10_full 100_half 100_full 1000_full
        # flow_control disable learning enable state enable mdix auto description SOMEDESCR

        medium_type = get_medium_type(tokens)
        for port_num in iter_ports(tokens[2]):
            # Config maybe different for copper and fiber ports
            if_name = self.interface_name(port_num) + medium_type
            yield self.make_interface(interface=if_name)

            rest_tokens = tokens[3:]
            skip = False
            for i, t in enumerate(rest_tokens):
                if skip:
                    skip = False
                    continue
                if t == "state":
                    skip = True
                    adm_status = "on" if rest_tokens[i + 1] == "enable" else "off"

                    yield self.make_interface_admin_status(
                        interface=if_name, admin_status=adm_status
                    )
                elif t == "description":
                    skip = True
                    desc = rest_tokens[i + 1]

                    yield self.make_interface_description(interface=if_name, description=desc)
                elif t == "flow_control":
                    skip = True
                    flow_state = "on" if rest_tokens[i + 1] == "enable" else "off"

                    yield self.make_interface_flow_control(
                        interface=if_name, flow_control=flow_state
                    )

    @match("enable", "sntp")
    def normalize_enable_sntp(self, tokens):
        yield self.make_clock_source(source="ntp")

    @match("disable", "sntp")
    def normalize_disable_sntp(self, tokens):
        yield self.make_clock_source(source="local")

    @match("config", "time_zone", "operator", ANY, "hour", INTEGER, "min", INTEGER)
    def normalize_tzoffset(self, tokens):
        """
        config time_zone operator + hour 3 min 0
        """
        offset = f"{tokens[-5]}{tokens[-3]}:{tokens[-1]}"
        yield self.make_tz_offset(tz_name="", tz_offset=offset)

    @match(
        "config", "sntp", "primary", IP_ADDRESS, "secondary", IP_ADDRESS, "poll-interval", INTEGER
    )
    def normalize_sntp_primary_secondary(self, tokens):
        """
        config sntp primary 172.25.0.126 secondary 22.22.22.22 poll-interval 720
        """
        yield self.make_ntp_server_address(name=tokens[3], address=tokens[3])
        yield self.make_ntp_server_prefer(name=tokens[3])
        yield self.make_ntp_server_address(name=tokens[5], address=tokens[5])

    @match("config", "sntp", "primary", IP_ADDRESS, REST)
    def normalize_sntp_primary(self, tokens):
        """
        config sntp primary 172.25.0.126 poll-interval 720
        """
        yield self.make_ntp_server_address(name=tokens[3], address=tokens[3])
        yield self.make_ntp_server_prefer(name=tokens[3])

    @match("create", "syslog", "host", INTEGER, "ipaddress", IP_ADDRESS, REST)
    def normalize_syslog_server(self, tokens):
        """
        create syslog host 1 ipaddress 172.16.0.1 severity critical facility local7 udp_port 514 state enable
        """
        yield self.make_protocols_syslog_server(ip=tokens[5])

    @match("config", "loopdetect", "ports", ANY, "state", ANY)
    def normalize_loopdetect(self, tokens):
        """
        config loopdetect ports 1:1 state disable
        config loopdetect ports 1:2 state enable
        """
        if tokens[-1] == "enable":
            for port_num in iter_ports(tokens[3]):
                if_name = self.interface_name(port_num)
                yield self.make_loop_detect_interface(interface=if_name)

    @match("create", "vlan", ANY, "tag", INTEGER)
    def normalize_vlans(self, tokens):
        """
        create vlan VLAN401 tag 401
        """
        yield self.make_vlan_name(vlan_id=tokens[-1], name=tokens[2])

    @match("enable", "stp")
    def normalize_enable_stp(self, tokens):
        yield self.make_global_spanning_tree_status(status="on")

    @match("disable", "stp")
    def normalize_disable_stp(self, tokens):
        yield self.make_global_spanning_tree_status(status="off")

    @match("create", "iproute", "default", IP_ADDRESS, REST)
    def normalize_def_gateway(self, tokens):
        """
        create iproute default 172.25.0.126 1 primary
        """
        yield self.make_inet_static_route_next_hop(route="0.0.0.0/0", next_hop=tokens[3])
