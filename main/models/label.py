# ----------------------------------------------------------------------
# Label model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List, Set, Iterable
from threading import Lock
import operator

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, IntField, BooleanField, ReferenceField
import cachetools

# NOC modules
from noc.core.model.decorator import on_save, on_delete
from noc.main.models.remotesystem import RemoteSystem


id_lock = Lock()


@on_save
@on_delete
class Label(Document):
    meta = {
        "collection": "labels",
        "strict": False,
        "auto_create_index": False,
    }

    name = StringField(unique=True)
    description = StringField()
    bg_color1 = IntField(default=0x000000)
    fg_color1 = IntField(default=0xFFFFFF)
    bg_color2 = IntField(default=0x000000)
    fg_color2 = IntField(default=0xFFFFFF)
    # Restrict UI operations
    is_protected = BooleanField(default=False)
    # Label scope
    enable_agent = BooleanField()
    enable_service = BooleanField()
    # Exposition scope
    expose_metric = BooleanField()
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = ReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Caches
    _name_cache = cachetools.TTLCache(maxsize=1000, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name: str) -> Optional["Label"]:
        return Label.objects.filter(name=name).first()

    def clean(self):
        # Wildcard labels are protected
        if self.is_wildcard:
            self.is_protected = True

    def on_save(self):
        if self.is_scoped and not self.is_wildcard:
            self._ensure_wildcards()

    def on_delete(self):
        if self.is_wildcard and any(Label.objects.filter(name__startswith=self.name[:-1])):
            raise ValueError("Cannot delete wildcard label with matched labels")

    @classmethod
    def merge_labels(cls, *args: List[str]) -> List[str]:
        """
        Merge sets of labels, processing the scopes.

        :param args:
        :return:
        """
        seen_scopes: Set[str] = set()
        seen: Set[str] = set()
        r: List[str] = []
        for labels in args:
            for label in labels:
                if label in seen:
                    continue
                elif "::" in label:
                    scope = label.rsplit("::", 1)[0]
                    if scope in seen_scopes:
                        continue
                    seen_scopes.add(scope)
                r.append(label)
                seen.add(label)
        return r

    @property
    def is_scoped(self) -> bool:
        """
        Returns True if the label is scoped
        :return:
        """
        return "::" in self.name

    @property
    def is_wildcard(self) -> bool:
        """
        Returns True if the label is protected
        :return:
        """
        return self.name.endswith("::*")

    def iter_scopes(self) -> Iterable[str]:
        """
        Yields all scopes
        :return:
        """
        r = []
        for p in self.name.split("::")[:-1]:
            r.append(p)
            yield "::".join(r)

    @classmethod
    def ensure_label(
        cls,
        name,
        description=None,
        is_protected=False,
        bg_color1=0xFFFFFF,
        fg_color1=0x000000,
        bg_color2=0xFFFFFF,
        fg_color2=0x000000,
    ) -> None:
        """
        Ensure label is exists, create when necessary
        :param name:
        :param description:
        :param is_protected:
        :param bg_color1:
        :param fg_color1:
        :param bg_color2:
        :param fg_color2:
        :return:
        """
        if Label.objects.filter(name=name).first():  # Do not use get_by_name. Cached None !
            return  # Exists
        Label(
            name=name,
            description=description or "Auto-created",
            is_protected=is_protected,
            bg_color1=bg_color1,
            fg_color1=fg_color1,
            bg_color2=bg_color2,
            fg_color2=fg_color2,
        ).save()

    def _ensure_wildcards(self):
        """
        Create all necessary wildcards for a scoped labels
        :return:
        """
        for scope in self.iter_scopes():
            # Ensure wildcard
            Label.ensure_label(
                f"{scope}::*",
                description=f"Wildcard label for scope {scope}",
                is_protected=True,
                bg_color1=self.bg_color1,
                fg_color1=self.fg_color1,
                bg_color2=self.bg_color2,
                fg_color2=self.fg_color2,
            )

    def get_matched_labels(self) -> List[str]:
        """
        Get list of matched labels for wildcard label
        :return:
        """
        label = self.name
        if label.endswith("::*"):
            return [
                x.name
                for x in Label.objects.filter(name__startswith=label[:-1]).only("name")
                if not x.name.endswith("::*")
            ]
        return [label]
