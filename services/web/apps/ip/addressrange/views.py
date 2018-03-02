# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ip.addressrange application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication
from noc.ip.models.addressrange import AddressRange
from noc.core.ip import IP
from noc.lib.validators import is_ipv4, is_ipv6, is_fqdn
from noc.core.translation import ugettext as _


class AddressRangeApplication(ExtModelApplication):
    """
    AddressRanges application
    """
    title = "Address Ranges"
    menu = [_("Setup"), _("Address Ranges")]
    model = AddressRange
    query_fields = ["name__icontains", "description__icontains"]

    def clean(self, data):
        data = super(AddressRangeApplication, self).clean(data)
        afi = data["afi"]
        from_address = data["from_address"]
        to_address = data["to_address"]
        # Check AFI
        address_validator = is_ipv4 if afi == "4" else is_ipv6
        if not address_validator(from_address):
            raise ValueError(
                "Invalid IPv%(afi)s 'From Address'" % {"afi": afi})
        if not address_validator(to_address):
            raise ValueError(
                "Invalid IPv%(afi)s 'To Address'" % {"afi": afi})
        # Check from address not greater than to address
        if IP.prefix(from_address) > IP.prefix(to_address):
            raise ValueError(
                "'To Address' must be greater or equal than 'From Address'")
        # Check for valid "action" combination
        if "fqdn_template" in data and data["fqdn_template"] and data["action"] != "G":
            raise ValueError(
                "'FQDN Template' must be clean for selected 'Action'")
        if "reverse_nses" in data and data["reverse_nses"] and data["action"] != "D":
            raise ValueError(
                "'Reverse NSes' must be clean for selected 'Action'")
        # Set range as locked for "G" and "D" actions
        if data["action"] != "N":
            data["is_locked"] = True
        # @todo: check FQDN template
        # Check reverse_nses is a list of FQDNs or IPs
        if "reverse_nses" in data and data["reverse_nses"]:
            reverse_nses = data["reverse_nses"]
            for ns in reverse_nses.split(","):
                ns = ns.strip()
                if not is_ipv4(ns) and not is_ipv6(ns) and not is_fqdn(
                        ns):
                    raise ValueError("%s is invalid nameserver" % ns)
        # Check no locked range overlaps another locked range
        if data["is_locked"]:
            r = [r for r in
                 AddressRange.get_overlapping_ranges(
                     data["vrf"],
                     data["afi"],
                     data["from_address"],
                     data["to_address"]
                 )
                 if r.is_locked is True]
            if r:
                raise ValueError("Locked range overlaps with ahother locked range: %s" % unicode(r[0]))
        return data
