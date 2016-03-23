# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Service
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
import logging
from collections import defaultdict
## Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, DateTimeField, DictField,
                                ReferenceField, IntField,
                                EmbeddedDocumentField, ListField,
                                ObjectIdField)
## NOC modules
from serviceprofile import ServiceProfile
from noc.crm.models.supplier import Supplier
from noc.crm.models.subscriber import Subscriber
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.lib.nosql import ForeignKeyField
from noc.sa.models.managedobject import ManagedObject
from noc.core.model.decorator import on_save, on_delete
from noc.models import get_object, get_model

logger = logging.getLogger(__name__)


class Service(Document):
    meta = {
        "collection": "noc.services",
        "indexes": [
            "subscriber"
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
