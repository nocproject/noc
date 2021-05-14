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
from noc.core.mongo.connection import get_db
from noc.core.model.decorator import on_save, on_delete
from noc.main.models.label import Label


id_lock = Lock()
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

    # Caches
    _name_cache = cachetools.TTLCache(maxsize=1000, ttl=60)
    _rx_compiled_cache = cachetools.TTLCache(maxsize=1000, ttl=60)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name: str) -> Optional["Label"]:
        return Label.objects.filter(name=name).first()

    @cachetools.cachedmethod(operator.attrgetter("_rx_compiled_cache"))
    def get_compiled(self, name: str) -> re.compile:
        """
        Cached compiled regex. name required for cache key (otherwise key is empty)
        :param name:
        :return:
        """
        rx = re.compile(self.regexp)
        if self.flag_multiline:
            rx.flags ^= re.MULTILINE
        if self.flag_dotall:
            rx.flags ^= re.DOTALL
        return rx

    # def clean(self):
    #     rx = Regex.from_native(self.regexp)
    #     rx.flags ^= re.UNICODE
    #     self.regexp_compiled = rx

    def iter_scopes(self) -> Iterable[str]:
        """
        Yields all scopes
        :return:
        """
        if self.enable_managedobject_name:
            yield "managedobject_name"
        if self.enable_managedobject_address:
            yield "managedobject_address"
        if self.enable_managedobject_description:
            yield "managedobject_description"
        if self.enable_interface_name:
            yield "interface_name"
        if self.enable_interface_description:
            yield "interface_description"

    # def get_labels(self, scope: str = None) -> List[str]:
    #     r = self.labels or []
    #     for scp in self.iter_scopes():
    #         if (scope and scp != scope) or not getattr(self, f"enable_{scp}", False):
    #             continue
    #         r += [f"noc::rxfilter::{self.name}::{scp}::="]
    #     return r

    @classmethod
    def get_effective_labels(cls, scope: str, value: str) -> List[str]:
        """
        :param: scope - check `enable_<scope>` for filter enable regex
        :param: value - string value for check
        """
        labels = []
        for rx in RegexpLabel.objects.filter(**{f"enable_{scope}": True}):
            if rx.get_compiled(rx.name).match(value):
                labels += [f"noc::rxfilter::{rx.name}::{scope}::="] + (rx.labels or [])
        return labels

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
        interface_labels, managed_object_labels = [], []
        # Sync scope
        for f in self._changed_fields:
            if not f.startswith("enable"):
                continue
            logger.info("[%s] Field scope %s changed. Reset effective labels", self.name, f)
            _, scope = f.split("_", 1)
            if scope.startswith("managedobject"):
                managed_object_labels += [f"noc::rxfilter::{self.name}::{scope}::="]
            elif scope.startswith("interface"):
                interface_labels += [f"noc::rxfilter::{self.name}::{scope}::="]
        if interface_labels:
            Label.reset_model_labels("inv.Interface", interface_labels)
        if managed_object_labels:
            Label.reset_model_labels("sa.ManagedObject", managed_object_labels)
        # Refresh regex
        if "regexp" in self._changed_fields:
            logger.info("[%s] Regex field change. Refresh labels", self.name)
            self._reset_caches()
            self._refresh_labels()
        elif "labels" in self._changed_fields:
            self._refresh_labels()

    def _refresh_labels(self):
        """
        Recalculate labels on model
        :return:
        """
        from django.db import connection

        for scope in self.iter_scopes():
            labels = [f"noc::rxfilter::{self.name}::{scope}::="] + (self.labels or [])
            model, field = scope.split("_")
            if model == "managedobject":
                # Cleanup current labels
                logger.info("[%s] Cleanup ManagedObject effective labels: %s", self.name, labels)
                Label.reset_model_labels("sa.ManagedObject", labels)
                # Apply new rule
                logger.info("[%s] Apply new regex '%s' labels", self.name, self.regexp)
                sql = f"""
                UPDATE sa_managedobject
                SET effective_labels=ARRAY (
                SELECT DISTINCT e FROM unnest(effective_labels || %s::varchar[]) AS a(e)
                )
                WHERE {field} ~ %s
                """
                cursor = connection.cursor()
                cursor.execute(sql, [labels, self.regexp])
            elif model == "interface":
                # Cleanup current labels
                logger.info("[%s] Cleanup Interface effective labels: %s", self.name, labels)
                Label.reset_model_labels("inv.Interface", labels)
                # Apply new rule
                coll = get_db()["noc.interfaces"]
                coll.bulk_write(
                    [
                        UpdateMany(
                            {field: {"$re": self.regexp}},
                            {"$addToSet": {"effective_labels": {"$each": labels}}},
                        )
                    ]
                )

    def _reset_caches(self):
        try:
            del self._rx_compiled_cache[self.name]
        except KeyError:
            pass
