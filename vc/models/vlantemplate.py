# ---------------------------------------------------------------------
# PhoneRange model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from threading import Lock
import operator
import logging

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    BooleanField,
    EmbeddedDocumentListField,
    ReferenceField,
)
from typing import Optional, Iterable, Tuple
from jinja2 import Template
import cachetools


# NOC modules
from noc.core.model.decorator import on_save, on_delete, on_delete_check
from noc.core.defer import defer
from noc.core.text import ranges_to_list
from .vlanprofile import VLANProfile
from .vlanfilter import VLANFilter


logger = logging.getLogger(__name__)
id_lock = Lock()


class VLANItem(EmbeddedDocument):
    # vlan = IntField(required=True, min_value=1, max_value=4095)
    vlan = StringField(required=True)
    name = StringField()  # Autogenerate ?
    description = StringField()
    profile = ReferenceField(VLANProfile, required=False)

    def __str__(self):
        return f"{self.vlan}: {self.name}"

    def clean(self):
        # Validate vlan and name
        VLANFilter.compile(self.vlan)
        Template(self.name).render({"vlan": 1})


@on_save
@on_delete
@on_delete_check(check=[("vc.L2DomainProfile", "template"), ("vc.L2Domain", "template")])
class VLANTemplate(Document):
    meta = {
        "collection": "vlantemplates",
        "strict": False,
        "auto_create_index": False,
    }

    name = StringField()
    description = StringField()
    type = StringField(
        choices=[("global", "Global"), ("l2domain", "L2 Domain"), ("manual", "Manual")],
        required=True,
    )
    vlans = EmbeddedDocumentListField(VLANItem)
    to_allocate_vlans = BooleanField(default=False)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id) -> Optional["VLANTemplate"]:
        return VLANTemplate.objects.filter(id=id).first()

    def on_save(self):
        # Allocate vlans when necessary
        if self.to_allocate_vlans:
            defer(
                "noc.vc.models.vlantemplate.allocate_vlans",
                template_id=str(self.id),
            )

    def iter_vlans(self) -> Iterable[Tuple[int, str, "VLANProfile"]]:
        """
        Iterate over vlans
        :return:
        """
        for vi in self.vlans:
            for vlan in ranges_to_list(vi.vlan):
                yield int(vlan), Template(vlan.name).render({"vlan": int(vlan)}), vi.profile

    def allocate_template(self):
        """

        :return:
        """
        from .vlan import VLAN

        for vlan_num, name, profile in self.iter_vlans():
            vlan = VLAN(vlan=vlan_num, name=name, profile=profile, l2domain=None)  # ?
            vlan.save()


def allocate_vlans(template_id):
    template = VLANTemplate.get_by_id(template_id)
    # Getting L2 Domain
    if not template:
        return
    template.allocate_vlans()
