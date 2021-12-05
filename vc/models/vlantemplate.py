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
from typing import Optional, Iterable, Tuple, List
from mongoengine.fields import StringField, BooleanField, ListField, ObjectIdField, EmbeddedDocumentListField, IntField, ReferenceField
from mongoengine.errors import ValidationError
import cachetools

# NOC modules
from noc.core.model.decorator import on_save, on_delete, on_delete_check
from noc.core.defer import defer
from noc.core.hash import hash_int
from .vlanprofile import VLANProfile


logger = logging.getLogger(__name__)
id_lock = Lock()


class VLANItem(EmbeddedDocument):
    vlan = IntField(required=True, min_value=1, max_value=4095)
    name = StringField() # Autogenerate ?
    description = StringField()
    profile = ReferenceField(VLANProfile, required=False)

    def __str__(self):
        return f"{self.vlan}: {self.name}"


@on_save
@on_delete
@on_delete_check(check=[("vc.L2DomainProfile", "template"), ("vc.L2Domain", "template")])
class VLANTemplate(Document):
    meta = {
        "collection": "vlantemplates",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            "parent",
            "static_service_groups",
            "effective_service_groups",
            "static_client_groups",
            "effective_client_groups",
        ],
    }

    name = StringField()
    description = StringField()
    type = StringField(
        choices=[
            ("global", "Global"),
            ("l2domain", "L2 Domain"),
            ("manual", "Manual")
        ],
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
                "noc.phone.models.phonerange.allocate_numbers",
                key=hash_int(self.id),
                range_id=str(self.id),
            )

    def iter_vlans(self) -> Iterable[Tuple[int, str, "VLANProfile"]]:
        """
        Iterate over vlans
        :return:
        """
        for n in range(int(self.from_number), int(self.to_number) + 1):
            yield str(n)

    def allocate_templates(self):
        """

        :return:
        """
        ...

def allocate_vlans(template_id):
    template = VLANTemplate.get_by_id(template_id)
    if not template:
        return
    template.allocate_vlans()
