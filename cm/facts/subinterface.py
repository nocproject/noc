# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import BaseFact


class SubInterface(BaseFact):
    ATTRS = ["name", "description", "admin_status",
             "[ipv4_addresses]", "[ipv6_addresses]",
             "ip_proxy_arp", "ip_redirects",
             "[tagged_vlans]", "untagged_vlan",
             "[protocols]", "[afi]",
             "input_ipv4_filter", "output_ipv4_filter"
             ]
    ID = ["name"]

    def __init__(self, name, interface=None, description=None,
                 admin_status=False, ip_proxy_arp=False, 
                 ip_redirects=False, tagged_vlans=None, 
                 untagged_vlan=None, ipv4_addresses=None,
                 ipv6_addresses=None, protocols=None, afi=None,
                 input_ipv4_filter=None, output_ipv4_filter=None,
                 **kwargs):
        super(SubInterface, self).__init__()
        self.name = name
        self.interface = interface
        self.description = description
        self.admin_status = admin_status
        self.has_description = False
        self.ipv4_addresses = ipv4_addresses
        self.ipv6_addresses = ipv6_addresses
        self.ip_proxy_arp = ip_proxy_arp
        self.ip_redirects = ip_redirects
        self.tagged_vlans = tagged_vlans
        self.untagged_vlan = untagged_vlan
        self.protocols = protocols
        self.afi = afi
        self.input_ipv4_filter = input_ipv4_filter
        self.output_ipv4_filter = output_ipv4_filter

    def __unicode__(self):
        return "SubInterface %s" % self.name

    @property
    def description(self):
        return self._description
    
    @description.setter
    def description(self, value):
        self._description = value or None
        
    @property
    def admin_status(self):
        return self._admin_status
    
    @admin_status.setter
    def admin_status(self, value):
        self._admin_status = bool(value)
        
    @property
    def has_description(self):
        return bool(self._description)
    
    @has_description.setter
    def has_description(self, value):
        pass

    @property
    def ipv4_addresses(self):
        return self._ipv4_addresses

    @ipv4_addresses.setter
    def ipv4_addresses(self, value):
        self._ipv4_addresses = value or []

    @property
    def ipv6_addresses(self):
        return self._ipv6_addresses

    @ipv6_addresses.setter
    def ipv6_addresses(self, value):
        self._ipv6_addresses = value or []

    @property
    def ip_proxy_arp(self):
        return self._ip_proxy_arp and bool(self.ipv4_addresses)
    
    @ip_proxy_arp.setter
    def ip_proxy_arp(self, value):
        self._ip_proxy_arp = bool(value)
        
    @property
    def ip_redirects(self):
        return self._ip_redirects and bool(self.ipv4_addresses)
    
    @ip_redirects.setter
    def ip_redirects(self, value):
        self._ip_redirects = bool(value)
        
    @property
    def tagged_vlans(self):
        return self._tagged_vlans
    
    @tagged_vlans.setter
    def tagged_vlans(self, value):
        if value:
            value = [int(v) for v in value]
        self._tagged_vlans = value or []

    @property
    def untagged_vlan(self):
        return self._untagged_vlan
    
    @untagged_vlan.setter
    def untagged_vlan(self, value):
        if value:
            value = int(value)
        self._untagged_vlan = value or None

    @property
    def protocols(self):
        return self._protocols

    @protocols.setter
    def protocols(self, value):
        self._protocols = value or []

    def add_protocol(self, protocol):
        if protocol not in self.protocols:
            self.protocols += [protocol]

    def remove_protocol(self, protocol):
        if protocol in self.protocols:
            self.protocols.remove(protocol)

    @property
    def afi(self):
        return self._afi

    @afi.setter
    def afi(self, value):
        self._afi = value or []

    def add_afi(self, afi):
        if afi not in self.afi:
            self.afi += [afi]

    def remove_afi(self, afi):
        if afi in self.afi:
            self.afi.remove(afi)

    @property
    def input_ipv4_filter(self):
        return self._input_ipv4_filter

    @input_ipv4_filter.setter
    def input_ipv4_filter(self, value):
        self._input_ipv4_filter = value or []

    @property
    def output_ipv4_filter(self):
        return self._output_ipv4_filter

    @output_ipv4_filter.setter
    def output_ipv4_filter(self, value):
        self._output_ipv4_filter = value or []
