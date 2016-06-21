# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NRI check
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## Third-party modules
import six
## NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.inv.models.interface import Interface
from noc.inv.models.extnrilink import ExtNRILink
from noc.sa.models.serviceprofile import ServiceProfile
from noc.sa.models.service import Service
from noc.inv.models.link import Link
from noc.sa.models.servicesummary import ServiceSummary
from noc.core.etl.portmapper.loader import loader as portmapper_loader


class NRICheck(DiscoveryCheck):
    """
    Network Resource Inventory integration
    """
    name = "nri"

    def handler(self):
        self.logger.info("NRI integration")
        # Check object has interfaces
        has_interfaces = "DB | Interfaces" in self.object.get_caps()
        if not has_interfaces:
            self.logger.info(
                "No interfaces discovered. "
                "Skipping interface status check"
            )
            return
        #
        self.interface_ops = {}  # id -> update op
        # Get NRI portmapper
        src_tags = [t[4:] for t in self.object.tags
                    if t.startswith("src:")]
        if len(src_tags) == 0:
            self.logger.info("Created directly. No NRI integration")
            return
        elif len(src_tags) > 1:
            self.logger.info(
                "Ambiguous NRI information (%s). Skipping checks",
                ", ".join(src_tags)
            )
            return
        self.nri = src_tags[0]
        pm = portmapper_loader.get_loader(self.nri)
        if not pm:
            self.logger.info("No portmapper for %s. Skipping checks",
                             src_tags[0])
            return
        self.portmapper = pm(self.object)
        # Load interfaces
        self.interfaces = {}
        for d in Interface._get_collection().find({
            "managed_object": self.object.id,
            "type": "physical"
        }, {
            "_id": 1,
            "name": 1,
            "nri_name": 1,
            "service": 1
        }):
            self.interfaces[d["_id"]] = d
        # Process tasks
        self.process_interfaces()
        self.process_links()
        self.process_services()
        # Apply batch job
        if self.interface_ops:
            self.logger.info("Applying %d batch writes", len(self.interface_ops))
            bulk = Interface._get_collection().initialize_unordered_bulk_op()
            for i in self.interface_ops:
                bulk.find({"_id": i}).update(self.interface_ops[i])
            bulk.execute()
            ServiceSummary.refresh_object(self.object)

    def interface_bulk_op(self, iface_id, op):
        def merge_dicts(d1, d2):
            for k in set(d1) | set(d2):
                if k in d1 and k in d2:
                    if isinstance(d1[k], dict) and isinstance(d2[k], dict):
                        yield k, dict(merge_dicts(d1[k], d2[k]))
                    else:
                        yield k, d2[k]
                elif k in d1:
                    yield k, d1[k]
                else:
                    yield k, d2[k]

        iop = self.interface_ops.get(iface_id, {})
        self.interface_ops[iface_id] = dict(merge_dicts(iop, op))
        if "$set" in op:
            for o in op["$set"]:
                self.interfaces[iface_id][o] = op["$set"][o]
        if "$unset" in op:
            for o in op["$unset"]:
                del self.interfaces[iface_id][o]

    def process_interfaces(self):
        """
        Fill Interface.nri_name
        """
        self.logger.info("Setting NRI names (%s)", self.nri)
        for i in six.itervalues(self.interfaces):
            nri_name = self.portmapper.to_remote(i["name"])
            if not nri_name:
                self.logger.info(
                    "Cannot map interface name '%s' to NRI '%s' (%s)",
                    i["name"], self.nri, self.object.platform
                )
            elif i.get("nri_name") != nri_name:
                self.logger.info("Mapping %s to %s", i["name"], nri_name)
                self.interface_bulk_op(i["_id"], {"$set": {"nri_name": nri_name}})

    def process_links(self):
        now = datetime.datetime.now()
        nc = ExtNRILink._get_collection()
        links = {}  # nri_name -> {dst_mo, dst_interface}
        for d in nc.find({
            "$or": [
                {"src_mo": self.object.id},
                {"dst_mo": self.object.id}
            ]
        }):
            if d["src_mo"] == d["dst_mo"] or d.get("ignore"):
                continue
            if d["src_mo"] == self.object.id:
                links[d["src_interface"]] = (d["dst_mo"], d["dst_interface"])
            else:
                links[d["dst_interface"]] = (d["src_mo"], d["src_interface"])
        if not links:
            self.logger.info("Nothing to link")
            return  # Nothing to link
        # Build nri_name -> name interface map
        nri_map = {}
        for i in six.itervalues(self.interfaces):
            n = i.get("nri_name")
            if n and n in links:
                nri_map[n] = i
        linked = {}
        for d in Link._get_collection().find({
            "interfaces": {
                "$in": [i["_id"] for i in six.itervalues(nri_map)]
            }
        }):
            for i in d["interfaces"]:
                linked[i] = d.get("discovery_method")
        # Process still unlinked interfaces
        for n in nri_map:
            if_name = nri_map[n]["name"]
            if nri_map[n]["_id"] in linked:
                self.logger.info(
                    "[%s|%s] Already linked via %s. Skipping",
                    if_name,
                    n,
                    linked[nri_map[n]["_id"]]
                )
                continue  # Already linked
            rmo, rnn = links[n]
            ri = Interface._get_collection().find_one({
                "managed_object": rmo,
                "nri_name": rnn
            }, {
                "_id": 1
            })
            if ri:
                xl = Link._get_collection().find_one({
                    "interfaces": ri["_id"]
                })
                if xl:
                    self.logger.info(
                        "[%s|%s] Remote interface is already linked via %s. Skipping",
                        if_name, n, xl.get("discovery_method")
                    )
                    continue
                self.logger.info("[%s|%s] Linking", if_name, n)
                Link._get_collection().insert({
                    "interfaces": [nri_map[n]["_id"], ri["_id"]],
                    "discovery_method": "nri",
                    "first_discovery": now,
                    "last_seen": now
                })
                # @todo: update_pop_links
                # @todo: update_uplinks
            else:
                self.logger.info(
                    "[%s|%s] Cannot find remote interface %s:%s. Skipping",
                    if_name, n, rmo, rnn
                )

    def process_services(self):
        """
        Bind services to interfaces
        """
        slist = [
            s for s in Service._get_collection().find({
                "managed_object": self.object.id,
                "nri_port": {
                    "$exists": True
                }
            }, {
                "_id": 1,
                "nri_port": 1,
                "profile": 1
            })
        ]
        smap = dict((s["nri_port"], s["_id"]) for s in slist)
        prof_map = dict(
            (s["_id"], ServiceProfile.get_by_id(s["profile"]))
             for s in slist
        )
        nmap = {}
        n = 0
        for i in six.itervalues(self.interfaces):
            if not i.get("nri_name"):
                continue
            if i["nri_name"] in smap:
                svc = smap[i["nri_name"]]
                if svc != i.get("service"):
                    self.logger.info(
                        "Binding service %s to interface %s",
                        svc, i["name"]
                    )
                    op = {
                        "service": svc
                    }
                    p = prof_map.get(svc)
                    if p and p.interface_profile:
                        op["profile"] = p.interface_profile.id
                    self.interface_bulk_op(i["_id"], {"$set": op})
                    n += 1
                del smap[i["nri_name"]]
            elif i.get("service"):
                self.logger.info(
                    "Removing service %s from interface %s",
                    i["service"], i["name"]
                )
                op = {
                    "service": ""
                }
                p = prof_map.get(i["service"])
                if p:
                    op["profile"] = ""

                self.interface_bulk_op(i["_id"], {"$unset": op})
            nmap[i["nri_name"]] = i
        for n in smap:
            svc = smap[n]
            if n not in nmap:
                self.logger.info(
                    "Cannot bind service %s. "
                    "Cannot find NRI interface %s",
                    svc, n
                )
                continue
            i = nmap[n]
            self.logger.info(
                "Binding service %s to interface %s",
                svc, i["name"]
            )
            op = {
                "service": svc
            }
            p = prof_map.get(svc)
            if p:
                op["profile"] = p.id
            self.interface_bulk_op(i["_id"], {"$set": op})
