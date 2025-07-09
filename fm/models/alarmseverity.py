# ---------------------------------------------------------------------
# AlarmSeverity model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from threading import Lock
from typing import Optional, Union, List
import operator

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document
from mongoengine.fields import StringField, IntField, UUIDField
import cachetools

# NOC modules
from noc.main.models.style import Style
from noc.core.model.decorator import on_delete_check
from noc.core.mongo.fields import ForeignKeyField
from noc.core.text import quote_safe_path
from noc.core.prettyjson import to_json

id_lock = Lock()


@on_delete_check(
    check=[
        ("fm.AlarmRule", "min_severity"),
        ("fm.AlarmRule", "max_severity"),
    ]
)
class AlarmSeverity(Document):
    """
    Alarm severities
    """

    meta = {
        "collection": "noc.alarmseverities",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["severity", "code"],
        "json_collection": "fm.alarmseverities",
        "json_unique_fields": ["name"],
    }
    name = StringField(required=True, unique=True)
    uuid = UUIDField(binary=True)
    description = StringField(required=False)
    severity = IntField(required=True)
    code = StringField(required=False)
    style = ForeignKeyField(Style)
    # Minimal alarm weight to reach severity
    min_weight = IntField(required=False)
    sound = StringField(default="alarm")
    volume = IntField(default=100)

    _id_cache = cachetools.TTLCache(maxsize=50, ttl=60)
    _code_cache = cachetools.TTLCache(maxsize=50, ttl=60)
    _css_cache = cachetools.TTLCache(maxsize=1000, ttl=600)
    _order_cache = {}
    _weight_cache = {}

    def __str__(self):
        return self.name

    def __gt__(self, other):
        return self.severity > other.severity

    def __ge__(self, other):
        return self.severity >= other.severity

    def __eq__(self, other):
        return self.severity == other.severity

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["AlarmSeverity"]:
        return AlarmSeverity.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_code_cache"), lock=lambda _: id_lock)
    def get_by_code(cls, code: str) -> Optional["AlarmSeverity"]:
        return AlarmSeverity.objects.filter(code=code).first()

    @classmethod
    def get_from_labels(cls, labels: List[str]) -> Optional["AlarmSeverity"]:
        """

        Args
            labels:

        """
        for ll in labels:
            if ll.startswith("noc::severity::"):
                return AlarmSeverity.get_by_code(ll[15:].upper())
        return None

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_order_cache"), lock=lambda _: id_lock)
    def get_ordered(cls) -> List["AlarmSeverity"]:
        """
        Returns list of severities ordered in acvending order
        :return:
        """
        return list(AlarmSeverity.objects.order_by("severity"))

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_weight_cache"), lock=lambda _: id_lock)
    def get_weights(cls):
        """
        Returns list of (weight, alpha)
        :return:
        """
        sevs = cls.get_ordered()
        weights = [(s.min_weight or 0) for s in sevs]
        severities = [s.severity for s in sevs]
        dw = [float(w1 - w0) for w0, w1 in zip(weights, weights[1:])]
        ds = [float(s1 - s0) for s0, s1 in zip(severities, severities[1:])]
        alpha = [(s / w if w else 0) for s, w in zip(ds, dw)]
        alpha += [alpha[-1]]
        return severities, weights, alpha

    @classmethod
    def get_severity(cls, severity) -> Optional["AlarmSeverity"]:
        """
        Returns Alarm Severity instance corresponding to numeric value
        """
        for s in reversed(cls.get_ordered()):
            if severity >= s.severity:
                return s
        return s

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_css_cache"), lock=lambda _: id_lock)
    def get_severity_css_class_name(cls, severity):
        return cls.get_severity(severity).style.css_class_name

    def get_json_path(self) -> str:
        return "%s.json" % quote_safe_path(self.name)

    def to_json(self) -> str:
        return to_json(
            {
                "name": self.name,
                "$collection": self._meta["json_collection"],
                "uuid": self.uuid,
                "description": self.description,
                "severity": self.severity,
                "min_weight": self.min_weight,
                "code": self.code,
                "style__name": self.style.name,
            },
            order=["name", "$collection", "uuid", "description", "severity", "style"],
        )

    @classmethod
    def severity_for_weight(cls, w) -> int:
        """
        Calculate absolute severity for given weight *w*
        :returns: severity as int
        """

        def find(weights, w):
            i = 0
            for i, mw in enumerate(weights):
                if w < mw:
                    return max(i - 1, 0)
            return i

        severities, weights, alpha = cls.get_weights()
        i = find(weights, w)
        return severities[i] + int(alpha[i] * (w - weights[i]))
