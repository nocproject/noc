# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Service catalog
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python module
from collections import namedtuple
## Third-party modules
import yaml


class ServiceCatalog(object):
    """
    High-level API to service catalog
    """

    NodeData = namedtuple("NodeData", ["listen", "node", "dc",
                                       "address", "port"])
    ServiceData = namedtuple("ServiceData", ["name", "external",
                                             "nodes", "listen"])

    def __init__(self, config="etc/noc.yml"):
        self.services = {}  # name -> data
        self.config = config
        self.load()

    def load(self):
        with open(self.config) as f:
            data = yaml.load(f)
        with open("ansible/config/services.yml") as f:
            sdata = yaml.load(f)
        # Fill node cache
        nodes = {}  # ip -> node data
        for n, nd in data["nodes"].iteritems():
            nodes[nd["address"]] = {
                "name": n,
                "dc": nd["datacenter"]
            }
        # Get system services
        external_services = set()
        for sn, sd in sdata["services"].iteritems():
            if sd.get("level") == "system":
                external_services.add(sn)
        # Fill service cache
        self.services = {}
        for sn, sd in data["services"].iteritems():
            # Enumerate nodes
            nd = []
            for a in sd:
                addr, port = a.split(":")
                node = nodes.get(addr)
                if node:
                    dc = node["dc"]
                    node = node["name"]
                else:
                    node = addr
                    dc = ""
                nd += [self.NodeData(
                    listen=a,
                    node=node,
                    dc=dc,
                    address=addr,
                    port=port
                )]
            self.services[sn] = self.ServiceData(
                name=sn,
                external=sn in external_services,
                listen=list(sd),
                nodes=nd
            )

    def get_services(self):
        return self.services.keys()

    def iter_services(self):
        for sn in self.services:
            yield sn

    def get_service(self, name):
        return self.services[name]
