# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Subscriber
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, ListField
# NOC modules
from .subscriberprofile import SubscriberProfile
from noc.main.models.remotesystem import RemoteSystem
from noc.lib.nosql import PlainReferenceField
from noc.wf.models.state import State


class Subscriber(Document):
    meta = {
        "collection": "noc.subscribers",
        "indexes": [
            "name"
        ],
        "strict": False,
        "auto_create_index": False
    }

    name = StringField()
    description = StringField()
    profile = PlainReferenceField(SubscriberProfile)
    state = PlainReferenceField(State)
    # Main address
    address = StringField()
    # Technical contacts
    tech_contact_person = StringField()
    tech_contact_phone = StringField()
    tags = ListField(StringField())
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = PlainReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()

    def __unicode__(self):
        return self.name
