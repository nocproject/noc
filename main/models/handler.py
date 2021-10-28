# ----------------------------------------------------------------------
# Approved handlers
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
import operator

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, BooleanField
import cachetools

# NOC modules
from noc.core.model.decorator import on_delete_check
from noc.core.handler import get_handler

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
        ("pm.ThresholdProfile", "umbrella_filter_handler"),
        ("pm.ThresholdProfile", "value_handler"),
        ("pm.ThresholdConfig", "open_handler"),
        ("pm.ThresholdConfig", "close_handler"),
        ("fm.AlarmGroupRule", "handler"),
    ]
)
class Handler(Document):
    meta = {"collection": "handlers", "strict": False, "auto_create_index": False}

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

    _id_cache = cachetools.TTLCache(maxsize=1000, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return Handler.objects.filter(id=id).first()

    def get_handler(self):
        return get_handler(self.handler)
