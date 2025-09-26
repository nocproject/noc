# ----------------------------------------------------------------------
# <describe module here>
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from ..box.prefix import PrefixCheck as BasePrefixCheck, DiscoveredPrefix, SRC_WHOIS_ROUTE


class PrefixCheck(BasePrefixCheck):
    def get_prefixes(self):
        # vpn_id, prefix => DiscoveredPrefix
        prefixes = {}
        prefixes = self.apply_prefixes(prefixes, self.get_whois_route_prefixes())
        return prefixes

    def get_whois_route_prefixes(self):
        prefixes = self.get_artefact("whois_route")
        if not prefixes:
            self.logger.info("No whois_route artefact, skipping whois route prefixes")
            return []
        profile = self.object.profile.prefix_profile_whois_route
        if not profile:
            self.logger.info("No prefix profile for whois route set. Skipping")
            return []
        return [
            DiscoveredPrefix(
                vpn_id="0:0",
                prefix=prefix,
                profile=profile,
                description=description,
                source=SRC_WHOIS_ROUTE,
                subinterface=None,
                vlan=None,
                asn=self.object,
            )
            for prefix, description in prefixes
        ]

    def is_enabled(self):
        return True
