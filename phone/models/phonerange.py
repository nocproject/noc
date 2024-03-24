# ---------------------------------------------------------------------
# PhoneRange model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from threading import Lock
from typing import Optional, Union
import operator
import logging

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document
from mongoengine.fields import StringField, BooleanField, ListField, ObjectIdField
from mongoengine.queryset import Q
from mongoengine.errors import ValidationError
import cachetools

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from noc.crm.models.supplier import Supplier
from noc.project.models.project import Project
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.core.mongo.fields import ForeignKeyField
from noc.wf.models.state import State
from noc.core.wf.decorator import workflow
from noc.core.model.decorator import on_save, on_delete, on_delete_check
from noc.core.defer import defer
from noc.core.hash import hash_int
from noc.core.text import clean_number
from noc.core.resourcegroup.decorator import resourcegroup
from .dialplan import DialPlan
from .phonerangeprofile import PhoneRangeProfile
from .numbercategory import NumberCategory

logger = logging.getLogger(__name__)
id_lock = Lock()
_path_cache = cachetools.TTLCache(maxsize=100, ttl=60)


@on_save
@resourcegroup
@workflow
@on_delete
@on_delete_check(check=[("phone.PhoneNumber", "phone_range"), ("phone.PhoneRange", "parent")])
class PhoneRange(Document):
    meta = {
        "collection": "noc.phoneranges",
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
    profile = PlainReferenceField(PhoneRangeProfile)
    state = PlainReferenceField(State)
    dialplan = PlainReferenceField(DialPlan)
    parent = PlainReferenceField("self")
    from_number = StringField()
    to_number = StringField()
    supplier = PlainReferenceField(Supplier)
    project = ForeignKeyField(Project)
    administrative_domain = ForeignKeyField(AdministrativeDomain)
    to_allocate_numbers = BooleanField()
    # Resource groups
    static_service_groups = ListField(ObjectIdField())
    effective_service_groups = ListField(ObjectIdField())
    static_client_groups = ListField(ObjectIdField())
    effective_client_groups = ListField(ObjectIdField())

    _id_cache = cachetools.TTLCache(100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["PhoneRange"]:
        return PhoneRange.objects.filter(id=oid).first()

    @cachetools.cached(_path_cache, key=lambda x: str(x.id), lock=id_lock)
    def get_path(self):
        """
        Returns list of parent range ids
        :return:
        """
        if self.parent:
            return self.parent.get_path() + [self.id]
        return [self.id]

    @classmethod
    def get_closest_range(cls, dialplan, from_number, to_number=None, exclude_range=None):
        """
        Find closest range enclosing given range
        :param dialplan:
        :param from_number:
        :param to_number:
        :param exclude_range:
        :return: Phone range or None
        """
        to_number = to_number or from_number
        if to_number < from_number:
            from_number, to_number = to_number, from_number
        q = {"dialplan": dialplan.id, "from_number__lte": from_number, "to_number__gte": to_number}
        if exclude_range:
            q["id__ne"] = exclude_range.id
        return PhoneRange.objects.filter(**q).order_by("-from_number", "to_number").first()

    def clean(self):
        self.from_number = clean_number(self.from_number or "")
        if not self.from_number:
            raise ValidationError("Empty from_number")
        self.to_number = clean_number(self.to_number or "")
        if not self.to_number:
            raise ValidationError("Empty to_number")
        if self.to_number < self.from_number:
            self.from_number, self.to_number = self.to_number, self.from_number
        super().clean()
        # Check overlapped ranges
        q = Q(dialplan=self.dialplan.id) & (
            Q(
                from_number__gt=self.from_number,
                from_number__lte=self.to_number,
                to_number__gt=self.to_number,
            )
            | Q(
                to_number__lt=self.to_number,
                from_number__lt=self.from_number,
                to_number__gte=self.from_number,
            )
            | Q(from_number=self.from_number, to_number=self.to_number)
        )
        if self.id:
            q &= Q(id__ne=self.id)
        rr = PhoneRange.objects.filter(q).first()
        if rr:
            raise ValidationError(
                "Overlapped ranges: %s - %s (%s)" % (rr.from_number, rr.to_number, rr.name)
            )
        q = {
            "dialplan": self.dialplan,
            "from_number": self.from_number,
            "to_number": self.to_number,
        }
        if self.id:
            q["exclude_range"] = self
        self.parent = PhoneRange.get_closest_range(**q)

    def on_save(self):
        from .phonenumber import PhoneNumber

        # Borrow own phone numbers from parent
        if self.parent:
            for n in PhoneNumber.objects.filter(
                phone_range=self.parent.id, number__gte=self.from_number, number__lte=self.to_number
            ):
                n.phone_range = self
                n.save()
        # Allocate numbers when necessary
        if self.to_allocate_numbers:
            defer(
                "noc.phone.models.phonerange.allocate_numbers",
                key=hash_int(self.id),
                range_id=str(self.id),
            )
        # Reparent nested ranges
        for r in PhoneRange.objects.filter(
            dialplan=self.dialplan,
            from_number__gte=self.from_number,
            from_number__lte=self.to_number,
            to_number__lte=self.to_number,
            id__ne=self.id,
        ):
            r.save()

    def on_delete(self):
        # Move nested phone numbers to parent
        from .phonenumber import PhoneNumber

        for n in PhoneNumber.objects.filter(phone_range=self.id):
            n.phone_range = self.parent
            n.save()
        # Move nested ranges to parent
        for r in PhoneRange.objects.filter(parent=self.id):
            r.parent = self.parent
            r.save()

    @property
    def has_children(self):
        return bool(PhoneRange.objects.filter(parent=self.id).first())

    @property
    def total_numbers(self):
        """
        Total phone numbers in range
        """
        return int(self.to_number) - int(self.from_number) + 1

    def iter_numbers(self):
        for n in range(int(self.from_number), int(self.to_number) + 1):
            yield str(n)

    def allocate_numbers(self):
        from .phonenumber import PhoneNumber

        # Alreacy created numbers
        existing_numbers = set(
            PhoneNumber.objects.filter(
                dialplan=self.dialplan.id, number__gte=self.from_number, number__lte=self.to_number
            ).values_list("number")
        )
        # Nested ranges
        nrxc = []
        for r in PhoneRange.objects.filter(parent=self.id):
            nrxc += ["(x >= '%s' and x <= '%s')" % (r.from_number, r.to_number)]
        if nrxc:
            nrx = compile(" or ".join(nrxc), "<string>", "eval")
        else:
            nrx = None
        #
        cat_rules = [cr for cr in NumberCategory.get_rules() if cr[0] == self.dialplan]
        # Create numbers
        for number in self.iter_numbers():
            if number in existing_numbers:
                continue
            if nrx and eval(nrx, {"x": number}):
                continue
            category = None
            for dp, rx_mask, c in cat_rules:
                if rx_mask.search(number):
                    category = c
                    break
            logger.info("[%s] Create number %s in category %s", self.name, number, category)
            n = PhoneNumber(
                dialplan=self.dialplan,
                number=number,
                category=category,
                profile=self.profile.default_number_profile,
            )
            n.save()


def allocate_numbers(range_id):
    range = PhoneRange.get_by_id(range_id)
    if not range:
        return
    range.allocate_numbers()
