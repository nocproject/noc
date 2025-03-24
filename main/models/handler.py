# ----------------------------------------------------------------------
# Approved handlers
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
from typing import Optional, Union, Dict, Any
import operator

# Third-party modules
import bson
from mongoengine.document import Document
from mongoengine.fields import StringField, BooleanField, UUIDField
import cachetools

# NOC modules
from noc.core.model.decorator import on_delete_check
from noc.core.handler import get_handler
from noc.core.prettyjson import to_json
from noc.core.text import quote_safe_path

id_lock = Lock()


@on_delete_check(
    check=[
        ("sa.ManagedObjectProfile", "resolver_handler"),
        ("sa.ManagedObjectProfile", "hk_handler"),
        ("sa.ManagedObjectProfile", "ifdesc_handler"),
        ("sa.ManagedObject", "config_filter_handler"),
        ("sa.ManagedObject", "config_diff_filter_handler"),
        ("sa.ManagedObject", "config_validation_handler"),
        ("inv.InterfaceProfile", "ifdesc_handler"),
        ("inv.TechDomain", "controller_handler"),
        ("pm.ThresholdProfile", "umbrella_filter_handler"),
        ("pm.ThresholdProfile", "value_handler"),
        ("fm.AlarmRule", "actions.handler"),
        ("fm.DispositionRule", "handlers.handler"),
        ("main.MessageRoute", "transmute_handler"),
    ]
)
class Handler(Document):
    meta = {
        "collection": "handlers",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "main.handlers",
    }
    uuid = UUIDField(binary=True)
    handler = StringField()
    name = StringField()
    description = StringField()
    allow_config_filter = BooleanField()
    allow_config_validation = BooleanField()
    allow_config_diff = BooleanField()
    allow_config_diff_filter = BooleanField()
    allow_housekeeping = BooleanField()
    allow_resolver = BooleanField()
    allow_threshold = BooleanField()
    allow_threshold_handler = BooleanField()
    allow_threshold_value_handler = BooleanField()
    allow_ds_filter = BooleanField()
    allow_ifdesc = BooleanField()
    allow_mx_transmutation = BooleanField()
    allow_match_rule = BooleanField()
    allow_fm_alarmgrouprule = BooleanField()
    allow_tech_domain = BooleanField()

    _id_cache = cachetools.TTLCache(maxsize=1000, ttl=60)

    def __str__(self):
        return self.name

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "uuid": self.uuid,
            "$collection": self._meta["json_collection"],
            "handler": self.handler,
            "name": self.name,
            "description": self.description,
            "allow_config_filter": self.allow_config_filter,
            "allow_config_validation": self.allow_config_validation,
            "allow_config_diff": self.allow_config_diff,
            "allow_config_diff_filter": self.allow_config_diff_filter,
            "allow_housekeeping": self.allow_housekeeping,
            "allow_resolver": self.allow_resolver,
            "allow_threshold": self.allow_threshold,
            "allow_threshold_handler": self.allow_threshold_handler,
            "allow_threshold_value_handler": self.allow_threshold_value_handler,
            "allow_ds_filter": self.allow_ds_filter,
            "allow_ifdesc": self.allow_ifdesc,
            "allow_mx_transmutation": self.allow_mx_transmutation,
            "allow_match_rule": self.allow_match_rule,
            "allow_fm_alarmgrouprule": self.allow_fm_alarmgrouprule,
        }
        return r

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=[
                "uuid",
                "$collection",
                "handler",
                "name",
                "description",
                "allow_config_filter",
                "allow_config_validation",
                "allow_config_diff",
                "allow_config_diff_filter",
                "allow_housekeeping",
                "allow_resolver",
                "allow_threshold",
                "allow_threshold_handler",
                "allow_threshold_value_handler",
                "allow_ds_filter",
                "allow_ifdesc",
                "allow_mx_transmutation",
                "allow_match_rule",
                "allow_fm_alarmgrouprule",
            ],
        )

    def get_json_path(self) -> str:
        return quote_safe_path(self.name.strip("*")) + ".json"

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, bson.ObjectId]) -> Optional["Handler"]:
        return Handler.objects.filter(id=oid).first()

    def get_handler(self):
        return get_handler(self.handler)
