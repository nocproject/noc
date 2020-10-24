# ----------------------------------------------------------------------
# ModelProtection Profile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
import operator
from collections import defaultdict

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import StringField, IntField, ListField, EmbeddedDocumentField
from mongoengine.errors import ValidationError
from mongoengine.queryset.visitor import Q
import cachetools

# NOC modules
from noc.models import get_model
from noc.aaa.models.group import Group
from noc.core.mongo.fields import ForeignKeyListField

MFAL_NONE = -1
MFAL_HIDDEN = 0
MFAL_DISABLE = 1
MFAL_RO = 2
MFDAL_MODIFY = 3

perm_lock = Lock()

FIELD_PERMISSIONS = {
    MFAL_HIDDEN: "Hidden",
    MFAL_DISABLE: "Disable",
    MFAL_RO: "Read-only",
    MFDAL_MODIFY: "Editable",
}


def check_model(model_name):
    try:
        get_model(model_name)
    except AssertionError:
        raise ValidationError


class FieldAccess(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    name = StringField()
    permission = IntField(choices=[(x, FIELD_PERMISSIONS[x]) for x in FIELD_PERMISSIONS])

    def __str__(self):
        return "%s:%s" % (self.name, self.permission)


class ModelProtectionProfile(Document):
    meta = {
        "collection": "noc.modelprotectionprofile",
        "strict": False,
        "auto_create_index": False,
    }

    name = StringField(required=True)
    description = StringField()
    model = StringField(validation=check_model, required=True)
    field_access = ListField(EmbeddedDocumentField(FieldAccess))
    groups = ForeignKeyListField(Group)

    _effective_perm_cache = cachetools.TTLCache(maxsize=100, ttl=3)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if "field_access" in getattr(self, "_changed_fields", []):
            # Check unique
            processed = set()
            access = []
            for fa in self.field_access:
                # Deduplicate rights
                if fa.name and fa.name in processed:
                    continue
                if fa.name:
                    # Split User and Group rights
                    access += [
                        FieldAccess(name=fa.name, permission=fa.permission),
                    ]
                    processed.add(fa.name)
                    continue
            self.field_access = access
        super().save()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_effective_perm_cache"), lock=lambda _: perm_lock)
    def get_effective_permissions(cls, model_id, user):
        """
        Returns a set of effective user permissions,
        counting group and implied ones
        """
        if user.is_superuser:
            return {}
        perms = defaultdict(list)

        for mpp in ModelProtectionProfile.objects.filter(
            model=model_id, groups__in=user.groups.all()
        ):
            for fa in mpp.field_access:
                perms[fa.name] += [fa.permission]
        return {p: max(perms[p]) for p in perms}

    @classmethod
    def has_editable(cls, model_id, user, field):
        query = Q(model=model_id, groups__in=list(user.groups.all()))
        query &= Q(
            __raw__={"field_access": {"$elemMatch": {"name": field, "permission": {"$lt": 3}}}}
        )
        return not ModelProtectionProfile.objects.filter(query).first()
