# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Firmware
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014=6 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, ReferenceField, ListField,
                                EmbeddedDocumentField)
# NOC modules
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from firmware import Firmware
from noc.lib.nosql import ForeignKeyField
from noc.lib.text import split_alnum


class ManagementPolicy(EmbeddedDocument):
    protocol = StringField(choices=[
        ("cli", "CLI"),
        ("snmp", "SNMP"),
        ("http", "HTTP")
    ])


class FirmwarePolicy(Document):
    meta = {
        "collection": "noc.firmwarepolicy",
        "allow_inheritance": False,
        "indexes": ["platform", "firmware"]
    }
    # Platform (Matched with get_version)
    platform = StringField()
    #
    description = StringField()
    #
    object_profile = ForeignKeyField(ManagedObjectProfile)
    #
    firmware = ReferenceField(Firmware)
    status = StringField(
        choices=[
            ("r", "Recommended"),
            ("a", "Acceptable"),
            ("n", "Not recommended"),
            ("d", "Denied")
        ]
    )
    #
    management = ListField(EmbeddedDocumentField(ManagementPolicy))

    @classmethod
    def get_status(cls, platform, version):
        for fp in FirmwarePolicy.objects.filter(platform=platform):
            if fp.firmware.version == version:
                return fp.status
        return None

    @classmethod
    def get_recommended_version(cls, platform):
        fp = FirmwarePolicy.objects.filter(platform=platform, status="r").first()
        if fp:
            return fp.firmware.version
        versions = []
        for fp in FirmwarePolicy.objects.filter(platform=platform, status="a"):
            versions += [fp.firmware.version]
        if versions:
            return sorted(versions,key=split_alnum)[-1]
        else:
            return None
