# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.ProCurve.get_spanning_tree
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetSpanningTree
#from noc.sa.interfaces.base import MACAddressParameter
from noc.lib.text import list_to_ranges
import re


class Script(noc.sa.script.Script):
    name = "HP.ProCurve.get_spanning_tree"
    implements = [IGetSpanningTree]

    ##
    ## walkMIB wrapper
    ## Return single value
    ##
    def mib_get(self, oid):
        v = self.cli("walkMIB %s" % oid)
        return v.split("=", 1)[1].strip()

    ##
    ## Returns hash of index->value
    ##
    def mib_walk(self, oid):
        r = {}
        last_id = None
        l_oid = len(oid) + 1
        for l in self.cli("walkMIB %s" % oid).splitlines():
            if l.startswith(oid):
                # New value
                k, v = [x.strip() for x in l.split("=", 1)]
                k = k[l_oid:]
                if "." not in k:
                    k = int(k)
                else:
                    k = tuple([int(x) for x in k.split(".")])
                r[k] = v
                last_id = k
            else:
                # Multi-line value
                r[last_id] += "\n" + l
        return r

    ##
    ## MSTP Parsing
    ##
    def process_mstp(self):
        r = {
            "mode": "MSTP",
            "instances": [],
            "configuration": {
                "MSTP": {
                    "region": self.mib_get("hpicfBridgeMSTRegionName"),
                    "revision": self.mib_get("hpicfBridgeMSTRegionRevision")
                }
            }
        }
        # Get bridge id
        bridge_id = self.mib_get("dot1dBaseBridgeAddress").replace(" ", "")
        bridge_id = "%s-%s" % (bridge_id[:6], bridge_id[6:])
        # Create instances
        instances = {}  # id -> {data}
        """
        instance id -> data: interface, port_id, state, role, priority,
        designated_bridge_id, designated_bridge_priority,
        designated_port_id, edge, point_to_point
        """
        interfaces = {}
        v = self.mib_walk("hpicfBridgeMSTInstanceRowStatus")
        for instance_id in v:
            if v[instance_id] == "1":
                instances[instance_id] = {"id": instance_id}
                interfaces[instance_id] = {}
        # Set root id and root priority
        v = self.mib_walk("hpicfBridgeMSTInstanceDesignatedRoot")
        for instance_id in v:
            if instance_id in instances:
                root = v[instance_id].replace(" ", "")
                root_priority = int(root[:2] + "00", 16)
                root = "%s-%s" % (root[4:10], root[10:])
                instances[instance_id]["root_id"] = root
                instances[instance_id]["root_priority"] = root_priority
        # Set bridge priority
        v = self.mib_walk("hpicfBridgeMSTInstancePriority")
        for instance_id in v:
            if instance_id in instances:
                instances[instance_id]["bridge_id"] = bridge_id
                instances[instance_id]["bridge_priority"] = v[instance_id].replace(",", "")
        # Get instance vlans
        vlans = {}  # instance -> vlans
        for i in [1, 2, 3, 4]:
            v = self.mib_walk("hpicfBridgeMSTInstanceVlanMap%dk" % i)
            for instance_id in v:
                if instance_id in instances:
                    try:
                        vlans[instance_id] += v[instance_id]
                    except KeyError:
                        vlans[instance_id] = v[instance_id]

        if not vlans.has_key(0):
            vlans[0] = ''
        # Convert bitmask to vlan list
        rest_vlans = set(range(1, 4096))
        for instance_id in vlans:
            v = set()
            for i, m in enumerate(vlans[instance_id].split()):
                m = int(m, 16)
                for j in range(8):
                    if m & (1 << (7 - j)):
                        vlan = i * 8 + j + 1
                        v.add(vlan)
                        rest_vlans.remove(vlan)
            vlans[instance_id] = v
        # Set instnace vlans
        for instance_id in vlans:
            v = vlans[instance_id]
            if not v and instance_id == 0:
                v = rest_vlans
            instances[instance_id]["vlans"] = list_to_ranges(sorted(v))
        #
        # Process interfaces
        #
        # port_id -> {"interface","port_id","edge","point_to_point"}
        ports = {}
        ifname = self.mib_walk("ifName")
        v = self.mib_walk("dot1dBasePortIfIndex")
        for port_id in v:
            ports[port_id] = {
                "interface": ifname[int(v[port_id])],
                "port_id": port_id
            }
        # Edge port status
        v = self.mib_walk("hpicfBridgeRstpOperEdgePort")
        for port_id in v:
            ports[port_id]["edge"] = v[port_id] == "1"
        # point_to_point status
        v = self.mib_walk("hpicfBridgeRstpOperPointToPointMac")
        for port_id in v:
            ports[port_id]["point_to_point"] = v[port_id] == "1"
        #
        # Process instance interfaces
        #
        instance_ports = {}  # instance_id -> port_id -> data
        for instance_id in instances:
            instance_ports[instance_id] = {}
            for port_id in ports:
                instance_ports[instance_id][port_id] = ports[port_id].copy()
        # Port priority
        v = self.mib_walk("hpicfBridgeMSTPortPriority")
        for instance_id, port_id in v:
            instance_ports[instance_id][port_id]["priority"] = v[instance_id, port_id]
        # Port state
        v = self.mib_walk("hpicfBridgeMSTPortState")
        for instance_id, port_id in v:
            instance_ports[instance_id][port_id]["state"] = {
                "1": "disabled",
                "2": "discarding",
                "??": "learning",
                "5": "forwarding",
                "_": "unknown"
            }[v[instance_id, port_id]]  # @todo: refine states
        # Port role
        v = self.mib_walk("hpicfBridgeMSTPortRole")
        for instance_id, port_id in v:
            instance_ports[instance_id][port_id]["role"] = {
                "1": "disabled",
                "?": "alternate",
                "5": "backup",
                "6": "disabled",
                "2": "root",
                "3": "designated",
                "_": "master",
                "__": "nonstp",
                "!!": "unknown"
            }[v[instance_id, port_id]]  # @todo: refine roles
        # Designated bridge
        v = self.mib_walk("hpicfBridgeMSTPortDesignatedBridge")
        for instance_id, port_id in v:
            bridge = v[instance_id, port_id].replace(" ", "")
            priority = int(bridge[:2] + "00", 16)
            bridge = "%s-%s" % (bridge[4:10], bridge[10:])
            instance_ports[instance_id][port_id]["designated_bridge_id"] = bridge
            instance_ports[instance_id][port_id]["designated_bridge_priority"] = priority
        # Designated port
        v = self.mib_walk("hpicfBridgeMSTPortDesignatedPort")
        for instance_id, port_id in v:
            x = v[instance_id, port_id]
            if " " in x:
                pr, p = x.split(" ")
                instance_ports[instance_id][port_id]["designated_port_id"] = "%d.%d" % (int(pr, 16), int(p, 16))
            else:
                instance_ports[instance_id][port_id]["designated_port_id"] = "%d.%d" % (ord(x[0]), ord(x[1]))
        # Fill missed designated bridge ids
        for instance_id in instance_ports:
            for port_id in instance_ports[instance_id]:
                v = instance_ports[instance_id][port_id]
                if "designated_bridge_id" not in v:
                    v["designated_bridge_id"] = bridge_id
                if "designated_bridge_priority" not in v:
                    v["designated_bridge_priority"] = 32768
        #
        # Install interfaces
        #
        for instance_id in instances:
            instances[instance_id]["interfaces"] = sorted(instance_ports[instance_id].values(), lambda x, y: cmp(x["port_id"], y["port_id"]))
        #
        # Install instances
        #
        r["instances"] = sorted(instances.values(), lambda x, y: cmp(x["id"], y["id"]))
        return r

    ##
    def process_rstp(self):
        r = {
            "mode": "RSTP"
        }
        # Get bridge id
        bridge_id = self.mib_get("dot1dBaseBridgeAddress").replace(" ", "")
        bridge_id = "%s-%s" % (bridge_id[:6], bridge_id[6:])

        # Create instances
        instance = {
            'id': 0,
            'vlans': "1-4095",
            'bridge_id': bridge_id
        }

        for l in self.cli('sh spanning-tree instance ist').splitlines():
            if l.find('Switch Priority') > 0:
                instance['bridge_priority'] = int(l.split(':')[1].strip())
            if l.find('Regional Root MAC Address') > 0:
                instance['root_id'] = l.split(':')[1].strip()
            if l.find('Regional Root Priority') > 0:
                instance['root_priority'] = int(l.split(':')[1].strip())

        # port_id -> {"interface","port_id","edge","point_to_point"}
        ports = {}
        ifname = self.mib_walk("ifName")
        v = self.mib_walk("dot1dBasePortIfIndex")
        for port_id in v:
            ports[port_id] = {
                "interface": ifname[int(v[port_id])],
                "port_id": port_id,
            }
        # Edge port status
        v = self.mib_walk("hpicfBridgeRstpOperEdgePort")
        for port_id in v:
            ports[port_id]["edge"] = v[port_id] == "1"
        # point_to_point status
        v = self.mib_walk("hpicfBridgeRstpOperPointToPointMac")
        for port_id in v:
            ports[port_id]["point_to_point"] = v[port_id] == "1"

        for bl in self.cli('sh spanning-tree instance ist detail').split('\n\n'):
            iface = {}
            for l in bl.splitlines():
                if l.find('Port') == 2:
                    iface['interface'] = l.split(':')[1].strip()
                if l.find('Role') > 0:
                    iface['role'] = l.split(':')[1].strip().lower()
                if l.find('State') > 0:
                    iface['state'] = l.split(':')[1].strip().lower()
                if l.find('Priority') == 2:
                    pri = l.split(':')[1].strip()
                    iface['priority'] = int(pri)
                if l.find('Designated Bridge ID') > 0:
                    iface['designated_bridge_priority'] = l.split(':')[1].lstrip()
                    iface['designated_bridge_id'] = l.split(':')[2].rstrip()
                if l.find('Designated Port ID') > 0:
                    iface['designated_port_id'] = l.split(':')[2].rstrip()

            if not iface:
                    continue

            for p in ports:
                    if iface['interface'] == ports[p]['interface']:
                        iface['port_id'] = '%s.%s' % (pri, ports[p]['port_id'])
                        iface['edge'] = ports[p]['edge']
                        iface['point_to_point'] = ports[p]['point_to_point']
            try:
                instance['interfaces'].append(iface)
            except KeyError:
                instance['interfaces'] = [iface]

        r["instances"] = [instance]
        return r

    def execute(self):
        stp_version = self.mib_get("hpicfBridgeRstpForceVersion")
        if stp_version == "1":
            # STP
            pass
        elif stp_version == "2":
            # RSTP
            return self.process_rstp()
        elif stp_version == "3":
            # MSTP
            return self.process_mstp()
