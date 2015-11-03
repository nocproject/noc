# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Version check
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck


class VersionCheck(DiscoveryCheck):
    """
    Version discovery
    """
    name = "version"
    required_script = "get_version"

    def handler(self):
        self.logger.info("Checking version")
        result = self.object.scripts.get_version()
        r = {}
        for k in result:
            v = result[k]
            if k == "attributes":
                for kk in v:
                    r[kk] = v[kk]
            else:
                r[k] = v
        for k in r:
            v = r[k]
            ov = self.object.get_attr(k)
            if ov != v:
                self.object.set_attr(k, v)
                self.logger.info("%s: %s -> %s", k, ov, v)
