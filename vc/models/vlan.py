# ----------------------------------------------------------------------
# VLAN
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
import operator
import logging

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (
    StringField,
    LongField,
    ListField,
    IntField,
    DateTimeField,
)
import cachetools

# NOC modules
from .vlanprofile import VLANProfile
from .l2domain import L2Domain
from noc.wf.models.state import State
from noc.project.models.project import Project
from noc.inv.models.networksegment import NetworkSegment
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.label import Label
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.core.wf.decorator import workflow
from noc.core.bi.decorator import bi_sync
from noc.core.model.decorator import on_delete_check, on_save

id_lock = Lock()
logger = logging.getLogger(__name__)


@Label.model
@bi_sync
@on_delete_check(check=[("vc.VLAN", "parent"), ("vc.L2Domain", "l2domain")])
@workflow
@on_save
class VLAN(Document):
    meta = {
        "collection": "vlans",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            {"fields": ["l2domain", "vlan"], "unique": True},
            "expired",
            "labels",
            "effective_labels",
        ],
    }

    name = StringField()
    profile = PlainReferenceField(VLANProfile)
    vlan = IntField(min_value=1, max_value=4095)
    l2domain = PlainReferenceField(L2Domain)
    description = StringField()
    state = PlainReferenceField(State)
    project = ForeignKeyField(Project)
    # Labels
    labels = ListField(StringField())
    effective_labels = ListField(StringField())
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = PlainReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Object id in BI
    bi_id = LongField(unique=True)
    # Discovery integration
    # Timestamp when object first discovered
    first_discovered = DateTimeField()
    # Timestamp when object last seen by discovery
    last_seen = DateTimeField()
    # Timestamp when send "expired" event
    expired = DateTimeField()

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return VLAN.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, id):
        return VLAN.objects.filter(bi_id=id).first()

    def clean(self):
        super().clean()
        self.segment = NetworkSegment.get_border_segment(self.segment)
        if self.translation_rule and not self.parent:
            self.translation_rule = None

    def refresh_translation(self):
        """
        Set VLAN translation according to segment settings
        :return:
        """
        if not self.apply_translation:
            return
        # Find matching rule
        for vt in self.segment.vlan_translation:
            if vt.filter.check(self.vlan):
                logger.debug(
                    "[%s|%s|%s] Matching translation rule <%s|%s|%s>",
                    self.segment.name,
                    self.name,
                    self.vlan,
                    vt.filter.expression,
                    vt.rule,
                    vt.parent_vlan.vlan,
                )
                if self.parent != vt.parent_vlan or self.translation_rule != vt.translation_rule:
                    self.modify(parent=vt.parent_vlan, translation_rule=vt.rule)
                return
        # No matching rule
        if self.parent or self.translation_rule:
            logger.debug("[%s|%s|%s] No matching translation rule, resetting")
            if self.parent or self.translation_rule:
                self.modify(parent=None, translation_rule=None)

    def on_save(self):
        self.refresh_translation()

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, "enable_vlan")
