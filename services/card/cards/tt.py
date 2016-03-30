# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## TT card handler
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## Third-party modules
import cachetools
## NOC modules
from base import BaseCard
from noc.fm.models.ttsystem import TTSystem


class TTCard(BaseCard):
    default_template_name = "tt"

    tts_cache = cachetools.TTLCache(
        maxsize=100,
        ttl=60,
        missing=lambda x: TTSystem.objects.filter(name=x).first()
    )

    def dereference(self, id):
        if ":" not in id:
            return None
        tts_name, tt_id = id.split(":", 1)
        tts = self.tts_cache[tts_name]
        if not tts:
            return None
        tt = tts.get_system().get_tt(tt_id)
        if tt:
            tt["tt_system_name"] = tts_name
            tt["full_id"] = id
            return tt
        else:
            return None

    def get_data(self):
        r = self.object.copy()
        if r["resolved"]:
            r["duration"] = r["close_ts"] - r["open_ts"]
        else:
            r["duration"] = datetime.datetime.now() - r["open_ts"]
        return r
