# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SelectorCache
## Updated by sa.refresh_selector_cache job
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.nosql import Document, IntField
from noc.lib.scheduler.utils import sliding_job


class SelectorCache(Document):
    meta = {
        "collection": "noc.cache.selector",
        "allow_inheritance": False,
        "indexes": ["object", "selector", "vc_domain"]
    }
    object = IntField(required=True)
    selector = IntField(required=False)
    vc_domain = IntField(required=False)

    def __unicode__(self):
        return "SelectorCache %s:%s" % (self.object, self.selector)

    @classmethod
    def refresh(cls):
        sliding_job("main.jobs", "sa.refresh_selector_cache", delta=5)
