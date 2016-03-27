# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlarmEscalation model
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, IntField, ReferenceField,
                                ListField, EmbeddedDocumentField)
## NOC modules
from noc.fm.models.alarmclass import AlarmClass
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.main.models.template import Template
from noc.main.models.notificationgroup import NotificationGroup
from ttsystem import TTSystem
from noc.lib.nosql import ForeignKeyField


class AlarmClassItem(EmbeddedDocument):
    alarm_class = ReferenceField(AlarmClass)


class EscalationItem(EmbeddedDocument):
    administrative_domain = ForeignKeyField(AdministrativeDomain)
    delay = IntField()
    template = ForeignKeyField(Template)
    notification_group = ForeignKeyField(NotificationGroup)
    tt_system = ReferenceField(TTSystem)
    tt_queue = StringField()


class AlarmEscalation(Document):
    """
    Alarm escalations
    """
    meta = {
        "collection": "noc.alarmescalatons",
        "allow_inheritance": False
    }

    name = StringField(unique=True)
    description = StringField()
    alarm_classes = ListField(EmbeddedDocumentField(AlarmClassItem))
    escalations = ListField(EmbeddedDocumentField(EscalationItem))
