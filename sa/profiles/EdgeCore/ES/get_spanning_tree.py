# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EdgeCore.ES.get_spanning_tree
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetspanningtree import IGetSpanningTree


class Script(BaseScript):
    name = "EdgeCore.ES.get_spanning_tree"
    interface = IGetSpanningTree

    rx_section = re.compile("^(?:-----*|\s*)\n", re.MULTILINE | re.DOTALL)

    TOKENS = {
        "spanning tree mode": "STP_MODE",
        "spanning tree enabled/disabled": "STP_ENABLED",
        "vlans configuration": "VLANS",
        "designated root": "DESG_ROOT",
        "designated bridge": "DESG_BRIDGE",
        "designated port": "DESG_PORT",
        "priority": "PRIORITY",
        "oper edge port": "EDGE_PORT",
        "role": "ROLE",
        "state": "STATE",
        "oper link type": "LINK_TYPE"
    }

    STATE_MAP = {
        "discarding": "discarding",
        "forwarding": "forwarding"
        # "disabled", "learning",
        # "broken", "listen", "unknown", "loopback"
    }
    ROLE_MAP = {
        "disabled": "disabled",
        "root": "root",
        "alternate": "alternate",
        "designate": "designated"
        # "backup",
        # "master", "nonstp", "unknown"
    }

    def iter_blocks(self, s):
        def parse_section(ss):
            sv = {}
            for l in ss.strip().splitlines():
                if ":" in l:
                    k, v = l.split(":", 1)
                    # Normalize names to known tokens
                    k = k.strip().lower()
                    k = self.TOKENS.get(k, k)
                    sv[k] = v.strip().lower()
            return sv

        sections = self.rx_section.split(s)
        yield None, parse_section(sections[1].strip())
        sections = sections[2:-1]
        while sections:
            sn = sections.pop(0).strip()
            sn = sn.replace("/ ", "/")
            sn = sn.split()
            ifname = " ".join(sn[:2])
            sv = parse_section(sections.pop(0).strip())
            yield ifname, sv

    def execute(self):
        r = self.cli("show spanning-tree")
        g = self.iter_blocks(r)
        _, cfg = g.next()
        if cfg["STP_ENABLED"].lower() != "enabled":
            # No STP
            return {
                "mode": "None",
                "instances": []
            }

        root_priority, root_id = cfg["DESG_ROOT"].split(".")

        instance = {
            "id": 0,
            "vlans": cfg["VLANS"],
            "bridge_id": "00:00:00:00:00:00",  # @todo: valid bridge_id,
            "bridge_priority": cfg["PRIORITY"],
            "root_id": root_id,
            "root_priority": int(root_priority),
            "interfaces": []
        }
        for sn, sv in g:
            desg_priority, desg_id = sv["DESG_BRIDGE"].split(".")
            iface = {
                "interface": sn,
                "port_id": "%s.%s" % (sv["PRIORITY"], sn.rsplit("/")[-1]),
                "role": self.ROLE_MAP[sv["ROLE"]],
                "state": self.STATE_MAP[sv["STATE"]],
                "priority": sv["PRIORITY"],
                "designated_bridge_id": desg_id,
                "designated_bridge_priority": desg_priority,
                "designated_port_id": sv["DESG_PORT"],
                "edge": sv["EDGE_PORT"] == "enabled",
                "point_to_point": sv["LINK_TYPE"] == "point-to-point"
            }
            instance["interfaces"] += [iface]
        return {
            "mode": cfg["STP_MODE"].upper(),
            "instances": [instance]
        }
