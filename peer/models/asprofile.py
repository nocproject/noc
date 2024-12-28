# ----------------------------------------------------------------------
# ASProfile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
from typing import Optional, Union, Dict, Any, Tuple, Callable
import operator

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    BooleanField,
    EmbeddedDocumentListField,
    ListField,
    IntField,
)
from mongoengine.errors import ValidationError
import cachetools

# NOC modules
from noc.core.model.decorator import on_delete_check
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.core.matcher import build_matcher
from noc.core.text import ranges_to_list
from noc.main.models.style import Style

id_lock = Lock()


class MatchRule(EmbeddedDocument):
    dynamic_order = IntField(default=0)
    labels = ListField(StringField())
    include_expression = StringField()

    def get_match_expr(self) -> Dict[str, Any]:
        r = {}
        if self.labels:
            r["labels"] = {"$all": list(self.labels)}
        if self.include_expression:
            r["asn"] = {"$any": ranges_to_list(self.include_expression)}
        return r

    def clean(self):
        if self.include_expression:
            try:
                ranges_to_list(self.include_expression)
            except (SyntaxError, ValueError):
                raise ValidationError(field_name="asn_ranges", message="Syntax Error on ASN Ranges")
        super().clean()


@on_delete_check(check=[("peer.AS", "profile")])
class ASProfile(Document):
    meta = {"collection": "asprofiles", "strict": False, "auto_create_index": False}

    name = StringField(unique=True)
    description = StringField()
    style = ForeignKeyField(Style, required=False)
    validation_policy = StringField(
        choices=[
            ("S", "Strict (Required RIR and Organisation)"),
            ("O", "Optional"),
        ],
        default="O",
    )
    gen_rpsl = BooleanField(default=False)

    enable_discovery_prefix_whois_route = BooleanField(default=False)
    enable_discovery_peer = BooleanField(default=True)
    prefix_profile_whois_route = PlainReferenceField("ip.PrefixProfile")
    # Dynamic Profile Classification
    dynamic_classification_policy = StringField(
        choices=[("R", "By Rule"), ("D", "Disable")],
        default="R",
    )
    # send_notification
    #
    match_rules = EmbeddedDocumentListField(MatchRule)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _default_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    DEFAULT_PROFILE_NAME = "default"

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["ASProfile"]:
        return ASProfile.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_default_cache"), lock=lambda _: id_lock)
    def get_default_profile(cls) -> "ASProfile":
        asp = ASProfile.objects.filter(name=cls.DEFAULT_PROFILE_NAME).first()
        if not asp:
            asp = ASProfile(name=cls.DEFAULT_PROFILE_NAME)
            asp.save()
        return asp

    def clean(self):
        if self.gen_rpsl and self.validation_policy != "S":
            raise ValidationError(message="RPSL Generate working only with validation_policy = 'S'")
        super().clean()

    def get_matcher(self) -> Callable:
        """"""
        expr = []
        for r in self.match_rules:
            expr.append(r.get_match_expr())
        if len(expr) == 1:
            return build_matcher(expr[0])
        return build_matcher({"$or": expr})

    def is_match(self, o) -> bool:
        """Local Match rules"""
        matcher = self.get_matcher()
        ctx = o.get_matcher_ctx()
        return matcher(ctx)

    @classmethod
    def get_profiles_matcher(cls) -> Tuple[Tuple[str, Callable], ...]:
        """Build matcher based on Profile Match Rules"""
        r = {}
        profiles = ASProfile.objects.filter(dynamic_classification_policy__ne="D")
        for pp in profiles:
            for mr in pp.match_rules:
                r[(str(pp.id), mr.dynamic_order)] = build_matcher(mr.get_match_expr())
        return tuple((x[0], r[x]) for x in sorted(r, key=lambda i: i[1]))
