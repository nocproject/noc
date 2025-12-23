# ----------------------------------------------------------------------
# project card
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.project.models.project import Project
from noc.ip.models.vrf import VRF
from noc.ip.models.prefix import Prefix
from noc.ip.models.address import Address
from noc.dns.models.dnszone import DNSZone
from noc.inv.models.interface import Interface
from noc.inv.models.subinterface import SubInterface
from noc.peer.models.asset import ASSet
from noc.peer.models.asn import AS
from noc.peer.models.peer import Peer
from noc.phone.models.phonerange import PhoneRange
from noc.phone.models.phonenumber import PhoneNumber
from noc.vc.models.vpn import VPN
from noc.vc.models.vlan import VLAN
from noc.crm.models.subscriber import Subscriber
from noc.crm.models.supplier import Supplier
from noc.sa.models.managedobject import ManagedObject
from .base import BaseCard


class ProjectCard(BaseCard):
    name = "project"
    default_template_name = "project"
    model = Project

    def get_data(self):
        # Get project's VRFs
        vrfs = list(VRF.objects.filter(project=self.object).order_by("name"))
        # Get project's Prefixes
        prefixes = list(Prefix.objects.filter(project=self.object).order_by("prefix"))
        # Get project's addresses
        addresses = list(Address.objects.filter(project=self.object).order_by("address"))
        # Get project's DNS zones
        dns_zones = list(DNSZone.objects.filter(project=self.object).order_by("name"))
        # Get project's managed objects
        managed_objects = list(ManagedObject.objects.filter(project=self.object).order_by("name"))
        # Get project's interfaces
        interfaces = list(Interface.objects.filter(project=self.object).order_by("name"))
        # Get project's subinterfaces
        sub_interfaces = list(SubInterface.objects.filter(project=self.object).order_by("name"))
        # Get project's ASes
        ases = list(AS.objects.filter(project=self.object).order_by("as_name"))
        # Get project's as-sets
        assets = list(ASSet.objects.filter(project=self.object).order_by("name"))
        # Get project's peers
        peers = list(Peer.objects.filter(project=self.object).order_by("profile"))
        # Get project's phone numbers
        phonenumbers = list(PhoneNumber.objects.filter(project=self.object).order_by("number"))
        # Get project'a phone ranges
        phoneranges = list(PhoneRange.objects.filter(project=self.object).order_by("name"))
        # Get project's phone numbers
        vpns = list(VPN.objects.filter(project=self.object).order_by("name"))
        # Get project'a phone ranges
        vlans = list(VLAN.objects.filter(project=self.object).order_by("id"))
        # Get project's subscribers
        subscribers = list(Subscriber.objects.filter(project=self.object).order_by("id"))
        # Get project's supplier
        suppliers = list(Supplier.objects.filter(project=self.object).order_by("id"))
        return {
            "object": self.object,
            "vrfs": vrfs,
            "prefixes": prefixes,
            "addresses": addresses,
            "dns_zones": dns_zones,
            "managed_objects": managed_objects,
            "interfaces": interfaces,
            "sub_interfaces": sub_interfaces,
            "ases": ases,
            "assets": assets,
            "peers": peers,
            "phonenumbers": phonenumbers,
            "phoneranges": phoneranges,
            "subscribers": subscribers,
            "suppliers": suppliers,
            "vpns": vpns,
            "vlans": vlans,
        }
