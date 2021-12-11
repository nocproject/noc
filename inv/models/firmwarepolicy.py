# ---------------------------------------------------------------------
# Firmware Policy
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Optional, List

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import StringField, ListField, EmbeddedDocumentField

# NOC modules
from noc.core.mongo.fields import ForeignKeyField, PlainReferenceField
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from .firmware import Firmware
from .platform import Platform


FS_RECOMMENDED = "r"
FS_ACCEPTABLE = "a"
FS_NOT_RECOMMENDED = "n"
FS_DENIED = "d"


PRIORITY_ORDER = [
    FS_DENIED,
    FS_NOT_RECOMMENDED,
    FS_ACCEPTABLE,
    FS_RECOMMENDED,
]


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
    condition = StringField(choices=["<", "<=", ">=", ">", "="], default="=")
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
    expose_labels = ListField(StringField())
    #
    management = ListField(EmbeddedDocumentField(ManagementPolicy))

    def __str__(self):
        return f"{self.platform}: {self.condition} {self.firmware.version}"

    @classmethod
    def get_status(cls, platform: "Platform", version: "Firmware") -> Optional[str]:
        if not platform or not version:
            return None
        fps = cls.get_effective_policies(platform, version)
        if fps:
            return list(sorted(fps, key=lambda x: PRIORITY_ORDER.index(x.status)))[0].status
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
            return list(sorted(versions))[-1]
        return None

    def is_fw_match(self, firmware: "Firmware"):
        """
        Check if firmware match Policy
        :param firmware:
        :return:
        """
        if not firmware:
            return True
        return (
            (self.condition == "<" and firmware < self.firmware)
            or (self.condition == "<=" and firmware <= self.firmware)
            or (self.condition == ">=" and firmware >= self.firmware)
            or (self.condition == ">" and firmware > self.firmware)
            or (self.condition == "=" and firmware == self.firmware)
        )

    @classmethod
    def get_effective_policies(
        cls, platform: "Platform", version: "Firmware" = None
    ) -> List["FirmwarePolicy"]:
        if not platform:
            return []
        fps = FirmwarePolicy.objects.filter(platform=platform.id)
        # if version:
        #    fps = [fp for fp in fps if fp.is_fw_match(version)]
        return [fp for fp in fps if fp.is_fw_match(version)]

    @classmethod
    def iter_lazy_labels(cls, firmware: "Firmware"):
        yield from FirmwarePolicy.get_effective_policies(version=firmware)
