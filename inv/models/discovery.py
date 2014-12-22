# !/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'boris'
## NOC modules
from noc.lib.nosql import (Document, StringField, ListField,
                           ForeignKeyField, DictField, DateTimeField,
                           IntField, FloatField)
from noc.sa.models.managedobject import ManagedObject


class Discovery(Document):
    meta = {
        "collection": "noc.schedules.inv.discovery",
        "allow_inheritance": False
    }

    job_class = StringField(db_field='jcls')
    schedule = DictField()
    ts = DateTimeField(db_field='ts')
    last = DateTimeField()
    last_success = DateTimeField(db_field='st')
    last_duration = FloatField(db_field='ldur')
    last_status = StringField(db_field='ls')
    status = StringField(db_field='s')
    managed_object = ForeignKeyField(ManagedObject, db_field='key')
    data = DictField()
    traceback = DictField()
    runs = IntField()
    faults = IntField(db_field='f')
    log = ListField()

    def __unicode__(self):
        return "%s: %s" % (self.managed_object, self.job_class)
