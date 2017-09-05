# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import datetime
import logging
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, DateTimeField,
                                ReferenceField, ListField, LongField)
# NOC modules
from .serviceprofile import ServiceProfile
from noc.crm.models.subscriber import Subscriber
from noc.main.models.remotesystem import RemoteSystem
from noc.lib.nosql import ForeignKeyField
from noc.sa.models.managedobject import ManagedObject
from noc.core.model.decorator import on_save, on_delete

logger = logging.getLogger(__name__)


@on_save
@on_delete
class Service(Document):
    meta = {
        "collection": "noc.services",
        "strict": False,
        "indexes": [
            "subscriber",
            "managed_object",
            "parent"
        ]
    }
    profile = ReferenceField(ServiceProfile, required=True)
    # Creation timestamp
    ts = DateTimeField(default=datetime.datetime.now)
    # Logical state of service
    logical_status = StringField(
            choices=[
                ("P", "Planned"),
                ("p", "Provisioning"),
                ("T", "Testing"),
                ("R", "Ready"),
                ("S", "Suspended"),
                ("r", "Removing"),
                ("C", "Closed"),
                ("U", "Unknown")
            ],
            default="U"
    )
    logical_status_start = DateTimeField()
    # Parent service
    parent = ReferenceField("self", required=False)
    # Subscriber information
    subscriber = ReferenceField(Subscriber)
    description = StringField()
    #
    agreement_id = StringField()
    # Order Fulfillment order id
    order_id = StringField()
    stage_id = StringField()
    stage_name = StringField()
    stage_start = DateTimeField()
    # Billing contract number
    account_id = StringField()
    # Connection address
    address = StringField()
    # For port services
    managed_object = ForeignKeyField(ManagedObject)
    # NRI port id, converted by portmapper to native name
    nri_port = StringField()
    # CPE information
    cpe_serial = StringField()
    cpe_mac = StringField()
    cpe_model = StringField()
    cpe_group = StringField()
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = ReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Object id in BI
    bi_id = LongField()
    #
    tags = ListField(StringField())

    def on_delete(self):
        if self.nri_port:
            self.unbind_interface()

    def on_save(self):
        if not hasattr(self, "_changed_fields") or "nri_port" in self._changed_fields:
            self.unbind_interface()
        if not hasattr(self, "_changed_fields") or "parent" in self._changed_fields:
            self._refresh_managed_object()

    def _refresh_managed_object(self):
        from noc.sa.models.servicesummary import ServiceSummary
        mo = self.get_managed_object()
        if mo:
            ServiceSummary.refresh_object(mo)

    def unbind_interface(self):
        from noc.inv.models.interface import Interface

        Interface._get_collection().update({
            "service": self.id
        }, {
            "$unset": {
                "service": ""
            }
        })
        self._refresh_managed_object()

    def get_managed_object(self):
        r = self
        while r:
            if r.managed_object:
                return self.managed_object
            r = r.parent
        return None
