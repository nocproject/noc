# ---------------------------------------------------------------------
# Firmware Policy
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
from typing import Optional, List

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import StringField, ListField, EmbeddedDocumentField
from mongoengine.queryset.visitor import Q
import cachetools

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from noc.main.models.label import Label
from .firmware import Firmware
from .platform import Platform

id_lock = Lock()

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


@Label.model
class FirmwarePolicy(Document):
    meta = {
        "collection": "noc.firmwarepolicy",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["platform", "firmware"],
    }
    # Platform (Matched with get_version)
    platform = PlainReferenceField(Platform, required=False)
    #
    description = StringField()
    #
    condition = StringField(choices=["<", "<=", ">=", ">", "="], default="=")
    #
    firmware = PlainReferenceField(Firmware, required=True)
    status = StringField(
        choices=[
            (FS_RECOMMENDED, "Recommended"),
            (FS_ACCEPTABLE, "Acceptable"),
            (FS_NOT_RECOMMENDED, "Not recommended"),
            (FS_DENIED, "Denied"),
        ]
    )
    #
    # Labels
    labels = ListField(StringField(max_length=250))
    effective_labels = ListField(StringField(max_length=250))
    #
    management = ListField(EmbeddedDocumentField(ManagementPolicy))

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _effective_policy_cache = cachetools.TTLCache(maxsize=100, ttl=600)

    def __str__(self):
        return f"{self.platform}: {self.condition} {self.firmware.version}"

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id) -> Optional["FirmwarePolicy"]:
        return FirmwarePolicy.objects.filter(id=id).first()

    @classmethod
    def get_status(
        cls, version: "Firmware", platform: Optional["Platform"] = None
    ) -> Optional[str]:
        if not version:
            return None
        fps = cls.get_effective_policies(version, platform)
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
        cls, version: "Firmware", platform: Optional["Platform"] = None
    ) -> List["FirmwarePolicy"]:
        """

        :param version:
        :param platform:
        :return:
        """
        if not version:
            return []
        q = Q(platform__exists=False)
        if platform:
            q |= Q(platform=platform.id)
        fps = FirmwarePolicy.objects.filter(q)
        return [fp for fp in fps if fp.is_fw_match(version)]

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, setting="enable_firmwarepolicy")
