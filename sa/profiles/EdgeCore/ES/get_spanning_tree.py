# ---------------------------------------------------------------------
# EdgeCore.ES.get_spanning_tree
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_spanning_tree import Script as BaseScript
from noc.sa.interfaces.igetspanningtree import IGetSpanningTree


class Script(BaseScript):
    name = "EdgeCore.ES.get_spanning_tree"
    interface = IGetSpanningTree

    rx_section = re.compile(r"^(?:-----*|\s*)\n", re.MULTILINE | re.DOTALL)
    rx_invalid_desg = re.compile(r"\.\d\.")
    rx_mstp = re.compile(
        r"^\s*Configuration Name\s*:\s*(?P<region>\S+)\s*\n"
        r"^\s*Revision Level\s*:\s*(?P<revision>\d+)",
        re.MULTILINE,
    )
    rx_instance = re.compile(r"^\s+(?P<instance>\d+)\s+\d+\S+\s*$", re.MULTILINE)

    TOKENS = {
        "spanning tree mode": "STP_MODE",
        "spanning tree enabled/disabled": "STP_ENABLED",
        "instance": "INSTANCE",
        "vlans configuration": "VLANS",
        "vlans configured": "VLANS",
        "designated root": "DESG_ROOT",
        "designated bridge": "DESG_BRIDGE",
        "designated port": "DESG_PORT",
        "priority": "PRIORITY",
        "oper edge port": "EDGE_PORT",
        "role": "ROLE",
        "state": "STATE",
        "oper link type": "LINK_TYPE",
    }
    STATE_MAP = {
        "discarding": "discarding",
        "forwarding": "forwarding",
        # "disabled", "learning",
        # "broken", "listen", "unknown", "loopback"
    }
    ROLE_MAP = {
        "disabled": "disabled",
        "disable": "disabled",
        "root": "root",
        "alternate": "alternate",
        "designate": "designated",
        "backup": "unknown",
        # "master", "nonstp", "unknown"
    }

    def iter_blocks(self, s):
        def parse_section(ss):
            sv = {}
            for line in ss.strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
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

    def parse_instance(self, cfg, g):
        # Sometimes crazy root ids like <root_priority>.0.<mac> is shown
        desg_root = self.rx_invalid_desg.sub(".", cfg["DESG_ROOT"])
        root_priority, root_id = desg_root.split(".")

        instance = {
            "id": 0,
            "vlans": cfg.get("VLANS", "1-4095"),
            "bridge_id": "00:00:00:00:00:00",  # @todo: valid bridge_id,
            "bridge_priority": cfg["PRIORITY"],
            "root_id": root_id,
            "root_priority": int(root_priority),
            "interfaces": [],
        }
        if cfg.get("INSTANCE"):
            instance["id"] = cfg.get("INSTANCE")
        for sn, sv in g:
            if sv.get("DESG_BRIDGE"):
                # Sometimes crazy bridge ids like <bridge_priority>.N.<mac> is shown
                desg_bridge = self.rx_invalid_desg.sub(".", sv.get("DESG_BRIDGE"))
                desg_priority, desg_id = desg_bridge.split(".")
            else:
                desg_priority, desg_id = None, None
                continue
            port_id = "%s.%s" % (sv.get("PRIORITY"), sn.rsplit("/")[-1])
            if sn.startswith("Trunk"):
                # Trunk interface
                port_id = sv.get("DESG_PORT")
            iface = {
                "interface": sn,
                "port_id": port_id,
                "role": self.ROLE_MAP[sv.get("ROLE", "disabled")],
                "state": self.STATE_MAP[sv.get("STATE", "forwarding")],
                "priority": sv.get("PRIORITY", 128),
                "designated_bridge_id": desg_id,
                "designated_bridge_priority": desg_priority,
                "designated_port_id": sv.get("DESG_PORT", None),
                "edge": sv.get("EDGE_PORT", "disabled") == "enabled",
                "point_to_point": sv.get("LINK_TYPE", None) == "point-to-point",
            }
            instance["interfaces"] += [iface]
        return instance

    def execute_cli(self, **kwargs):
        r = self.cli("show spanning-tree")
        g = self.iter_blocks(r)
        _, cfg = next(g)
        if cfg["STP_ENABLED"].lower() != "enabled":
            # No STP
            return {"mode": "None", "instances": []}

        res = {"mode": cfg["STP_MODE"].upper(), "instances": []}
        res["instances"] += [self.parse_instance(cfg, g)]

        if cfg["STP_MODE"].upper() == "MSTP":
            v = self.cli("show spanning-tree mst configuration")
            match = self.rx_mstp.search(v)
            if match:
                res["configuration"] = {
                    "MSTP": {"region": match.group("region"), "revision": match.group("revision")}
                }
            for inst in self.rx_instance.finditer(v):
                if int(inst["instance"]) == 0:
                    continue
                r = self.cli("show spanning-tree mst %s" % inst["instance"])
                g = self.iter_blocks(r)
                _, cfg = next(g)
                res["instances"] += [self.parse_instance(cfg, g)]

        return res
