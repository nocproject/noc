# ----------------------------------------------------------------------
# MeasurementUnits document model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
from typing import Optional

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import StringField, IntField, UUIDField, ListField, EmbeddedDocumentField
import cachetools

# NOC modules
from noc.core.model.decorator import on_delete_check
from noc.core.prettyjson import to_json
from noc.core.text import quote_safe_path


id_lock = Lock()


class AltUnit(EmbeddedDocument):
    # Unique units name
    name = StringField()
    # Optional description
    description = StringField()
    # Short label
    label = StringField()
    # Label for dashboards
    dashboard_label = StringField()
    # Expression to convert from primary units to alternative.
    # Primary value is denoted as variable x
    from_primary = StringField()
    # Expression to convert from alternative units to primary.
    # Alternative value is denoted as variable x
    to_primary = StringField()

    def __str__(self):
        return self.name

    @property
    def json_data(self):
        return {
            "name": self.name,
            "description": self.description,
            "label": self.label,
            "dashboard_label": self.dashboard_label,
            "from_primary": self.from_primary,
            "to_primary": self.to_primary,
        }


class EnumValue(EmbeddedDocument):
    key = StringField()
    value = IntField()

    def __str__(self):
        return f"{self.key}: {self.value}"

    @property
    def json_data(self):
        return {"key": self.key, "value": self.value}


@on_delete_check(check=[("inv.Sensor", "units")])
class MeasurementUnits(Document):
    meta = {
        "collection": "measurementunits",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "pm.measurementunits",
        "json_unique_fields": ["name"],
    }

    # Unique units name
    name = StringField(unique=True)
    # Global ID
    uuid = UUIDField(binary=True)
    # Optional description
    description = StringField()
    # Short label
    label = StringField()
    # Label for dashboards
    dashboard_label = StringField()
    # Type of scale (K/M/G prefixes)
    # * d - decimal scale, 1/1_000/1_000_000/...
    # * b - binary scale,  1/2^10/2^20/...
    scale_type = StringField(choices=["d", "b"], default="d")
    # Alternative units
    alt_units = ListField(EmbeddedDocumentField(AltUnit))
    # Enumerations
    enum = ListField(EmbeddedDocumentField(EnumValue))

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id) -> Optional["MeasurementUnits"]:
        return MeasurementUnits.objects.filter(id=id).first()

    @property
    def json_data(self):
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "label": self.label,
            "dashboard_label": self.dashboard_label,
            "scale_type": self.scale_type,
        }
        if self.description:
            r["description"] = self.description
        if self.alt_units:
            r["alt_units"] = [x.json_data for x in self.alt_units]
        if self.enum:
            r["enum"] = [x.json_data for x in self.enum]
        return r

    def to_json(self):
        return to_json(
            self.json_data,
            order=[
                "name",
                "$collection",
                "uuid",
                "description",
                "label",
                "dashboard_label",
                "scale_type",
                "alt_units",
                "enum",
            ],
        )

    def get_json_path(self):
        return "%s.json" % quote_safe_path(self.name)
