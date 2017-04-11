# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Outage Extractor
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## NOC modules
from base import BaseExtractor
from noc.fm.models.reboot import Reboot
from noc.sa.models.managedobject import ManagedObject
from noc.core.bi.models.reboots import Reboots
from noc.core.etl.bi.stream import Stream


class RebootsExtractor(BaseExtractor):
    name = "reboots"
    extract_delay = int(os.environ.get(
        "NOC_BI_EXTRACT_DELAY_REBOOTS", 3600
    ))
    clean_delay = int(os.environ.get(
        "NOC_BI_CLEAN_DELAY_REBOOTS", 86400
    ))

    def __init__(self, prefix, start, stop):
        super(RebootsExtractor, self).__init__(prefix, start, stop)
        self.reboot_stream = Stream(Reboots, prefix)

    def extract(self):
        for d in Reboot._get_collection().find({
            "ts": {
                "$gt": self.start,
                "$lte": self.stop
            }
        }, timeout=False).sort("ts"):
            mo = ManagedObject.get_by_id(d["object"])
            if not mo:
                continue
            version = mo.version
            self.reboot_stream.push(
                ts=d["ts"],
                managed_object=mo,
                pool=mo.pool,
                ip=mo.address,
                profile=mo.profile_name,
                object_profile=mo.object_profile,
                vendor=mo.vendor,
                platform=mo.platform,
                version=version.version,
                administrative_domain=mo.administrative_domain,
                segment=mo.segment,
                container=mo.container,
                x=mo.x,
                y=mo.y
            )
            self.last_ts = d["ts"]
        self.reboot_stream.finish()

    def clean(self):
        Reboot._get_collection().remove({
            "ts": {
                "$lte": self.clean_ts
            }
        })
