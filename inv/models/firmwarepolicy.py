# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Firmware Policy
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import StringField, ListField, EmbeddedDocumentField

# NOC modules
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from .firmware import Firmware
from .platform import Platform
from noc.core.mongo.fields import ForeignKeyField, PlainReferenceField
from noc.core.text import alnum_key


FS_RECOMMENDED = "r"
FS_ACCEPTABLE = "a"
FS_NOT_RECOMMENDED = "n"
FS_DENIED = "d"


class ManagementPolicy(EmbeddedDocument):
    protocol = StringField(choices=[("cli", "CLI"), ("snmp", "SNMP"), ("http", "HTTP")])


class FirmwarePolicy(Document):
    meta = {
        "collection": "noc.firmwarepolicy",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["platform", "firmware"],
    }
    # Platform (Matched with get_version)
    platform = PlainReferenceField(Platform)
    #
    description = StringField()
    #
    object_profile = ForeignKeyField(ManagedObjectProfile)
    #
    firmware = PlainReferenceField(Firmware)
    status = StringField(
        choices=[
            (FS_RECOMMENDED, "Recommended"),
            (FS_ACCEPTABLE, "Acceptable"),
            (FS_NOT_RECOMMENDED, "Not recommended"),
            (FS_DENIED, "Denied"),
        ]
    )
    #
    management = ListField(EmbeddedDocumentField(ManagementPolicy))

    @classmethod
    def get_status(cls, platform, version):
        if not platform or not version:
            return None
        fp = FirmwarePolicy.objects.filter(platform=platform.id, firmware=version.id).first()
        if fp:
            return fp.status
        else:
            return None

    @classmethod
    def get_recommended_version(cls, platform):
        """
        Get recommended version for  platform

        :param platform: Platform instance
        :return: Version string or None
        """
        if not platform:
            return None
        fp = FirmwarePolicy.objects.filter(platform=platform.id, status=FS_RECOMMENDED).first()
        if fp:
            return fp.firmware.version
        versions = []
        for fp in FirmwarePolicy.objects.filter(platform=platform.id, status=FS_ACCEPTABLE):
            versions += [fp.firmware.version]
        if versions:
            # Get latest acceptable version
            return list(sorted(versions, key=lambda x: alnum_key(x)))[-1]
        return None
