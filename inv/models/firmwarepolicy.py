# ---------------------------------------------------------------------
# Firmware Policy
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
from typing import Optional, List, Dict, Any, Union

# Third-party modules
import bson
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import StringField, ListField, EmbeddedDocumentField, IntField
from mongoengine.queryset.visitor import Q
import cachetools

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from noc.core.model.decorator import on_save, on_delete
from noc.main.models.label import Label
from noc.core.cache.base import cache
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


@on_delete
@on_save
@Label.model
class FirmwarePolicy(Document):
    meta = {
        "collection": "noc.firmwarepolicy",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            "platform",
            "firmware",
            {"fields": ("platform", "firmware", "condition"), "unique": True},
        ],
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
    # Object Discovery Settings
    access_preference = StringField(
        max_length=8,
        choices=[
            # ("P", "Profile"),
            ("S", "SNMP Only"),
            ("C", "CLI Only"),
            ("SC", "SNMP, CLI"),
            ("CS", "CLI, SNMP"),
        ],
        required=False,
    )
    snmp_rate_limit = IntField(default=0)
    #
    management = ListField(EmbeddedDocumentField(ManagementPolicy))

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _effective_policy_cache = cachetools.TTLCache(maxsize=100, ttl=600)

    def __str__(self):
        return f"{self.platform}: {self.condition} {self.firmware.version}"

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, bson.ObjectId]) -> Optional["FirmwarePolicy"]:
        return FirmwarePolicy.objects.filter(id=oid).first()

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

    def on_save(self):
        from noc.sa.models.managedobject import CREDENTIAL_CACHE_VERSION

        access_change = hasattr(self, "_changed_fields") and (
            "access_preference" in self._changed_fields or "snmp_rate_limit" in self._changed_fields
        )
        if access_change or (not hasattr(self, "_changed_fields") and self.access_preference):
            cache.delete_many(
                [f"cred-{x}" for x in self.get_affected_managed_objects_ids()],
                version=CREDENTIAL_CACHE_VERSION,
            )

        labels = [
            ll for ll in self.labels if Label.get_effective_setting(ll, "enable_managedobject")
        ]
        if not labels:
            return
        if (
            not hasattr(self, "_changed_fields")
            or "labels" in self._changed_fields
            or "firmware" in self._changed_fields
            or "condition" in self._changed_fields
        ):
            Label.add_model_labels(
                "sa.ManagedObject",
                labels=labels,
                instance_filters=[
                    ("version", [str(fw.id) for fw in self.get_affected_firmwares()])
                ],
            )
            # self.set_labels(labels)

    def on_delete(self):
        if self.labels:
            Label.remove_model_labels(
                "sa.ManagedObject",
                labels=self.labels,
                instance_filters=[
                    ("version", [str(fw.id) for fw in self.get_affected_firmwares()])
                ],
            )
            # self.reset_labels()

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
            return fp.firmware
        versions = []
        for fp in FirmwarePolicy.objects.filter(platform=platform.id, status=FS_ACCEPTABLE):
            versions += [fp.firmware]
        if versions:
            # Get latest acceptable version
            return sorted(versions, key=operator.attrgetter("version"))[-1]
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
        return list(
            sorted(
                [fp for fp in fps if fp.is_fw_match(version)], key=operator.attrgetter("firmware")
            )
        )

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, setting="enable_firmwarepolicy")

    def get_affected_firmwares(self) -> List["Firmware"]:
        r = [
            fw
            for fw in Firmware.objects.filter(profile=self.firmware.profile)
            if self.is_fw_match(fw)
        ]
        return r

    def get_affected_managed_objects_ids(self) -> List[int]:
        from noc.sa.models.managedobject import ManagedObject

        firmwares = self.get_affected_firmwares()
        if not firmwares:
            return []
        return list(
            ManagedObject.objects.filter(version__in=firmwares).values_list("id", flat=True)
        )

    def set_labels(self, labels: List[str] = None):
        from django.db import connection

        fws = [str(fw.id) for fw in self.get_affected_firmwares()]
        sql = """
        UPDATE sa_managedobject
        SET effective_labels=ARRAY (
        SELECT DISTINCT e FROM unnest(effective_labels || %s::varchar[]) AS a(e)
        )
        WHERE version = ANY (%s::text[])
        """
        cursor = connection.cursor()
        cursor.execute(sql, [labels or self.labels, fws])

    def reset_labels(self):
        from django.db import connection

        fws = [str(fw.id) for fw in self.get_affected_firmwares()]

        sql = """
        UPDATE sa_managedobject
         SET effective_labels=array(
         SELECT unnest(effective_labels) EXCEPT SELECT unnest(%s::varchar[])
         ) WHERE effective_labels && %s::varchar[] AND version = ANY (%s::text[])
         """
        cursor = connection.cursor()
        cursor.execute(sql, [self.labels, self.labels, fws])

    @property
    def object_settings(self) -> Dict[str, Any]:
        r = {}
        if self.access_preference:
            r["access_preference"] = self.access_preference
        if self.snmp_rate_limit:
            r["snmp_rate_limit"] = self.snmp_rate_limit
        return r
