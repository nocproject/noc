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
from noc.sa.models.objectpath import ObjectPath
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
            path = ObjectPath.get_path(mo)
            x, y = mo.get_coordinates()
            self.reboot_stream.push(
                ts=d["ts"],
                object_id=str(mo.id),
                object_name=mo.name,
                ip=mo.address,
                profile=mo.profile_name,
                object_profile_id=str(mo.object_profile.id),
                object_profile_name=mo.object_profile.name,
                vendor=mo.vendor,
                platform=mo.platform,
                version=version.version,
                adm_path=[str(p) for p in path.adm_path] if path else [],
                segment_path=path.segment_path if path else [],
                container_path=path.container_path if path else [],
                x=x,
                y=y
            )
            self.last_ts = d["ts"]
        self.reboot_stream.finish()

    def clean(self):
        Reboot._get_collection().remove({
            "ts": {
                "$lte": self.clean_ts
            }
        })
