# ---------------------------------------------------------------------
# PhoneRange model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from threading import Lock
from typing import Iterable, Optional, Tuple, Union
import operator
import logging

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    BooleanField,
    EmbeddedDocumentListField,
    ReferenceField,
)
from mongoengine.queryset.visitor import Q
from jinja2 import Template
import cachetools


# NOC modules
from noc.core.model.decorator import on_save, on_delete_check
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
@on_delete_check(check=[("vc.L2DomainProfile", "vlan_template"), ("vc.L2Domain", "vlan_template")])
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

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["VLANTemplate"]:
        return VLANTemplate.objects.filter(id=oid).first()

    def on_save(self):
        # Allocate vlans when necessary
        if self.to_allocate_vlans:
            defer(
                "noc.vc.models.vlantemplate.allocate_vlans",
                template_id=str(self.id),
            )

    def iter_vlans(self) -> Iterable[Tuple[int, str, str, "VLANProfile"]]:
        """
        Iterate over template vlans
        :return:
        """
        for vi in self.vlans:
            for vlan in ranges_to_list(vi.vlan):
                yield int(vlan), Template(vi.name).render(
                    {"vlan": int(vlan)}
                ), vi.description, vi.profile

    def allocate_template(self, l2_domain: str):
        """

        :return:
        """
        from .vlan import VLAN

        # @todo L2Domain pools filter ?
        existing_vlans = set(VLAN.objects.filter(l2_domain=l2_domain).values_list("vlan"))
        for vlan_num, name, description, profile in self.iter_vlans():
            if vlan_num in existing_vlans:
                continue
            vlan = VLAN(
                vlan=vlan_num,
                name=name,
                description=description,
                profile=profile,
                l2_domain=l2_domain,
            )
            vlan.save()


def allocate_vlans(template_id):
    from noc.vc.models.l2domain import L2Domain
    from noc.vc.models.l2domainprofile import L2DomainProfile

    template = VLANTemplate.get_by_id(template_id)
    if not template:
        logger.warning("VLAN Template with id: %s does not exist", template_id)
        return
    # Getting L2 Domain
    q = Q(vlan_template=template_id)
    profiles = list(L2DomainProfile.objects.filter(vlan_template=template_id).values_list("id"))
    if profiles:
        q |= Q(id__in=profiles)

    for l2d in L2Domain.objects.filter(q):
        template.allocate_template(l2d.id)
