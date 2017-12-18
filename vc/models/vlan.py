# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# VLAN
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from threading import Lock
import operator
import logging
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, LongField, ListField, IntField, BooleanField
import cachetools
# NOC modules
from .vlanprofile import VLANProfile
from .vpn import VPN
from noc.wf.models.state import State
from noc.project.models.project import Project
from noc.inv.models.networksegment import NetworkSegment
from noc.main.models.remotesystem import RemoteSystem
from noc.lib.nosql import PlainReferenceField, ForeignKeyField
from noc.core.wf.decorator import workflow
from noc.core.bi.decorator import bi_sync
from noc.core.model.decorator import on_delete_check, on_save

id_lock = Lock()
logger = logging.getLogger(__name__)


@bi_sync
@on_delete_check(check=[
    ("vc.VLAN", "parent")
])
@workflow
@on_save
class VLAN(Document):
    meta = {
        "collection": "vlans",
        "strict": False,
        "auto_create_index": False
    }

    name = StringField(unique=True)
    profile = PlainReferenceField(VLANProfile)
    vlan = IntField(min_value=1, max_value=4095)
    segment = PlainReferenceField(NetworkSegment)
    description = StringField()
    state = PlainReferenceField(State)
    project = ForeignKeyField(Project)
    # Link to gathering VPN
    vpn = PlainReferenceField(VPN)
    # VxLAN VNI
    vni = IntField()
    # Translation rules when passing border
    translation_rule = StringField(choices=[
        # Rewrite tag to parent vlan's
        ("map", "map"),
        # Append parent tag as S-VLAN
        ("push", "push")
    ])
    #
    parent = PlainReferenceField("self")
    # Automatically apply segment translation rule
    apply_translation = BooleanField(default=True)
    # List of tags
    tags = ListField(StringField())
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = PlainReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Object id in BI
    bi_id = LongField(unique=True)
    # @todo: last_seen
    # @todo: expired

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __unicode__(self):
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
        super(VLAN, self).clean()
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
            if vt.filter.match(self.vlan):
                logger.debug(
                    "[%s|%s|%s] Matching translation rule <%s|%s|%s>",
                     self.segment.name, self.name, self.vlan,
                     vt.filter.expression, vt.translation_rule,
                     vt.parent.name)
                if self.parent != vt.parent_vlan or self.translation_rule != vt.translation_rule:
                    self.modify(
                        parent=vt.parent_vlan,
                        translation_rule=vt.translation_rule
                    )
                return
        # No matching rule
        if self.parent or self.translation_rule:
            logger.debug("[%s|%s|%s] No matching translation rule, resetting")
            if self.parent or self.translation_rule:
                self.modify(
                    parent=None,
                    translation_rule=None
                )

    def on_save(self):
        self.refresh_translation()
