## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PMCheck model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC Modules
from noc.lib.nosql import (Document, StringField, DictField,
                           BooleanField, PlainReferenceField,
                           IntField)
from probe import PMProbe
from storage import PMStorage
from noc.pm.pmprobe.checks.base import check_registry
from noc.lib.scheduler.utils import sliding_job


class PMCheck(Document):
    """
    PM Check
    """
    meta = {
        "collection": "noc.pm.check",
        "allow_inheritance": False
    }
    name = StringField(unique=True)
    is_active = BooleanField(default=True)
    probe = PlainReferenceField(PMProbe)
    storage = PlainReferenceField(PMStorage)
    check = StringField(choices=check_registry.choices)
    config = DictField()
    interval = IntField()

    def __unicode__(self):
        return self.name

    @property
    def handler(self):
        return check_registry[self.check]

    def save(self, *args, **kwargs):
        from ts import PMTS
        super(PMCheck, self).save(*args, **kwargs)
        # Create time series
        for t in self.handler.get_time_series(self.config):
            if not PMTS.objects.filter(check=self, name=t.name).first():
                PMTS(
                    name=t.name,
                    storage=self.storage,
                    check=self,
                    type=t.type
                ).save()
        # Notify changes
        self.touch(self.id)

    @classmethod
    def touch(cls, id):
        sliding_job("main.jobs", "pm.touch_check", key=id)
