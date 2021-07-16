# ----------------------------------------------------------------------
# RegexLabel model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List, Iterable
from threading import Lock
import re
import logging
import operator

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, BooleanField, ListField
from pymongo import UpdateMany
import cachetools

# from bson.regex import Regex

# NOC modules
from noc.core.model.decorator import on_save, on_delete
from noc.main.models.label import Label


id_lock = Lock()
re_lock = Lock()
logger = logging.getLogger(__name__)


@on_save
@on_delete
@Label.match_labels(category="rxfilter", allowed_op={"="})
class RegexpLabel(Document):
    meta = {
        "collection": "regexlabels",
        "strict": False,
        "auto_create_index": False,
    }

    name = StringField(unique=True)
    description = StringField()
    # Regular Expresion
    regexp = StringField(required=True)
    regexp_compiled = StringField(required=False)
    # Set Multiline flag
    flag_multiline = BooleanField(default=False)
    # Set DotAll flag
    flag_dotall = BooleanField(default=False)
    # Set labels if match regex
    labels = ListField(StringField())
    # Allow apply for ManagedObject
    enable_managedobject_name = BooleanField(default=False)
    enable_managedobject_address = BooleanField(default=False)
    enable_managedobject_description = BooleanField(default=False)
    # Allow apply for Interface
    enable_interface_name = BooleanField(default=False)
    enable_interface_description = BooleanField(default=False)
    # Allow apply for Interface
    enable_sensor_local_id = BooleanField(default=False)

    # Caches
    _name_cache = cachetools.TTLCache(maxsize=1000, ttl=60)
    _re_cache = {}

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name: str) -> Optional["Label"]:
        return Label.objects.filter(name=name).first()

    @cachetools.cachedmethod(operator.attrgetter("_re_cache"), lock=lambda _: re_lock)
    def _get_re(self, pattern: str) -> Optional[re.Pattern]:
        try:
            rx = re.compile(pattern)
        except re.error:
            return None
        if self.flag_multiline:
            rx.flags ^= re.MULTILINE
        if self.flag_dotall:
            rx.flags ^= re.DOTALL
        return rx

    @classmethod
    def get_effective_labels(cls, scope: str, value: str) -> List[str]:
        """
        :param: scope - check `enable_<scope>` for filter enable regex
        :param: value - string value for check
        """
        labels = []
        for rx in RegexpLabel.objects.filter(**{f"enable_{scope}": True}):
            if rx._get_re(rx.regexp).match(value):
                labels += [f"noc::rxfilter::{rx.name}::="] + (rx.labels or [])
        return labels

    # def clean(self):
    #     rx = Regex.from_native(self.regexp)
    #     rx.flags ^= re.UNICODE
    #     self.regexp_compiled = rx

    def iter_models_fields(self) -> Iterable[str]:
        """
        Yields all scopes
        :return:
        """
        if self.enable_managedobject_name:
            yield "sa.ManagedObject", "name"
        if self.enable_managedobject_address:
            yield "sa.ManagedObject", "address"
        if self.enable_managedobject_description:
            yield "sa.ManagedObject", "description"
        if self.enable_interface_name:
            yield "inv.Interface", "name"
        if self.enable_interface_description:
            yield "inv.Interface", "description"
        if self.enable_sensor_local_id:
            yield "inv.Sensor", "local_id"

    # def get_labels(self, scope: str = None) -> List[str]:
    #     r = self.labels or []
    #     for scp in self.iter_scopes():
    #         if (scope and scp != scope) or not getattr(self, f"enable_{scp}", False):
    #             continue
    #         r += [f"noc::rxfilter::{self.name}::{scp}::="]
    #     return r

    def on_save(self):
        """
        Sync field changes to model
        For scope change:
          * Remove label from model
        For Regex change:
          * Update labels set for regex
        For labels change:
          * Sync label for change
        :return:
        """
        if not hasattr(self, "_changed_fields"):
            return
        # print(self._old_values)
        # Refresh regex
        if (
            "regexp" in self._changed_fields
            or "flag_multiline" in self._changed_fields
            or "flag_dotall" in self._changed_fields
        ):
            logger.info("[%s] Regex field change. Refresh labels", self.name)
            self._reset_caches()
            self._refresh_labels()

    def _refresh_labels(self):
        """
        Recalculate labels on model
        :return:
        """
        from django.db import connection
        from noc.models import get_model, is_document

        labels = [f"noc::rxfilter::{self.name}::="] + (self.labels or [])
        for model_id, field in self.iter_models_fields():
            model = get_model(model_id)
            if is_document(model):
                # Cleanup current labels
                logger.info("[%s] Cleanup Interface effective labels: %s", self.name, labels)
                Label.reset_model_labels(model_id, labels)
                # Apply new rule
                coll = model._get_collection()
                coll.bulk_write(
                    [
                        UpdateMany(
                            {field: {"$regex": self.regexp}},
                            {"$addToSet": {"effective_labels": {"$each": labels}}},
                        )
                    ]
                )
            else:
                # Cleanup current labels
                logger.info("[%s] Cleanup ManagedObject effective labels: %s", self.name, labels)
                Label.reset_model_labels(model_id, labels)
                # Apply new rule
                logger.info("[%s] Apply new regex '%s' labels", self.name, self.regexp)
                sql = f"""
                UPDATE {model._meta.db_table}
                SET effective_labels=ARRAY (
                SELECT DISTINCT e FROM unnest(effective_labels || %s::varchar[]) AS a(e)
                )
                WHERE {field} ~ %s
                """
                cursor = connection.cursor()
                cursor.execute(sql, [labels, self.regexp])

    def _reset_caches(self):
        try:
            del self._re_cache[self.regexp]
        except KeyError:
            pass
