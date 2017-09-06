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
from noc.bi.models.reboots import Reboots
from noc.core.etl.bi.stream import Stream
from noc.config import config


class RebootsExtractor(BaseExtractor):
    name = "reboots"
    extract_delay = config.bi.extract_delay_reboots
    clean_delay = config.bi.clean_delay_reboots

    def __init__(self, prefix, start, stop):
        super(RebootsExtractor, self).__init__(prefix, start, stop)
        self.reboot_stream = Stream(Reboots, prefix)

    def extract(self):
        nr = 0
        for d in Reboot._get_collection().find({
            "ts": {
                "$gt": self.start,
                "$lte": self.stop
            }
        }, no_cursor_timeout=True).sort("ts"):
            mo = ManagedObject.get_by_id(d["object"])
            if not mo:
                continue
            self.reboot_stream.push(
                ts=d["ts"],
                managed_object=mo,
                pool=mo.pool,
                ip=mo.address,
                profile=mo.profile,
                object_profile=mo.object_profile,
                vendor=mo.vendor,
                platform=mo.platform,
                version=mo.version,
                administrative_domain=mo.administrative_domain,
                segment=mo.segment,
                container=mo.container,
                x=mo.x,
                y=mo.y
            )
            nr += 1
            self.last_ts = d["ts"]
        self.reboot_stream.finish()
        return nr

    def clean(self):
        Reboot._get_collection().remove({
            "ts": {
                "$lte": self.clean_ts
            }
        })

    @classmethod
    def get_start(cls):
        d = Reboot._get_collection().find_one(
            {},
            {"_id": 0, "ts": 1},
            sort=[("ts", 1)]
        )
        if not d:
            return None
        return d.get("ts")
