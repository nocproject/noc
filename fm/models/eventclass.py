# ---------------------------------------------------------------------
# EventClass model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import os
from threading import Lock
from typing import Optional, Union, List
import operator

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    BooleanField,
    IntField,
    LongField,
    ListField,
    DictField,
    ObjectIdField,
    EnumField,
    EmbeddedDocumentListField,
    EmbeddedDocumentField,
    UUIDField,
)
from mongoengine.errors import ValidationError
import cachetools
import jinja2

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from noc.core.escape import json_escape as q
from noc.core.text import quote_safe_path
from noc.core.handler import get_handler
from noc.core.model.decorator import on_delete_check
from noc.core.bi.decorator import bi_sync
from noc.core.change.decorator import change
from noc.core.models.valuetype import ValueType
from noc.config import config
from .alarmclass import AlarmClass

id_lock = Lock()
handlers_lock = Lock()


class EventClassVar(EmbeddedDocument):
    meta = {"strict": False}
    name = StringField(required=True)
    description = StringField(required=False)
    type: ValueType = EnumField(ValueType, required=True)
    required = BooleanField(required=True)
    match_suppress = BooleanField(default=False)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return (
            self.name == other.name
            and self.description == other.description
            and self.type == other.type
            and self.required == other.required
            and self.match_suppress == other.match_suppress
        )


class EventDispositionRule(EmbeddedDocument):
    meta = {"strict": False}
    # Name, unique within event class
    name = StringField(required=True, default="dispose")
    # Python logical expression to check do the rules
    # applicable or not.
    condition = StringField(required=True, default="True")
    # Python logical expression to evaluate managed object
    managed_object = StringField(required=False)
    # What to do with disposed event:
    #    drop - delete and stop disposition
    #    ignore - stop disposition
    #    pyrule - execute pyrule
    #    raise - raise an alarm
    #    clear - clear alarm
    #
    action = StringField(
        required=True, choices=[(x, x) for x in ("drop", "ignore", "raise", "clear")]
    )
    # Applicable for actions: raise and clear
    alarm_class = PlainReferenceField(AlarmClass, required=False)
    # Additional condition. Raise or clear action
    # will be performed only if additional events occurred during time window
    combo_condition = StringField(
        required=False,
        default="none",
        choices=[
            (x, x)
            for x in (
                # Apply action immediately
                "none",
                # Apply when event firing rate
                # exceeds combo_count times during combo_window
                "frequency",
                # Apply action if event followed by all combo events
                # in strict order
                "sequence",
                # Apply action if event followed by all combo events
                # in no specific order
                "all",
                # Apply action if event followed by any of combo events
                "any",
            )
        ],
    )
    # Time window for combo events in seconds
    combo_window = IntField(required=False, default=0)
    # Applicable for frequency.
    combo_count = IntField(required=False, default=0)
    # Applicable for sequence, all and any combo_condition
    combo_event_classes = ListField(
        PlainReferenceField("fm.EventClass"), required=False, default=[]
    )
    # event var name -> alarm var name mappings
    # try to use direct mapping if not set explicitly
    var_mapping = DictField(required=False)
    # Stop event disposition if True or continue with next rule
    stop_disposition = BooleanField(required=False, default=True)

    def __str__(self):
        return "%s: %s" % (self.action, self.alarm_class.name)

    def __eq__(self, other):
        for a in [
            "name",
            "condition",
            "action",
            "pyrule",
            "window",
            "var_mapping",
            "stop_disposition",
            "managed_object",
        ]:
            if hasattr(self, a) != hasattr(other, a):
                return False
            if hasattr(self, a) and getattr(self, a) != getattr(other, a):
                return False
        if self.alarm_class is None and other.alarm_class is None:
            return True
        if (
            self.alarm_class is None
            or other.alarm_class is None
            or self.alarm_class.name != other.alarm_class.name
        ):
            return False
        return True


class EventPlugin(EmbeddedDocument):
    meta = {"strict": False}

    name = StringField()
    config = DictField(default={})

    def __str__(self):
        return self.name


class EventClassCategory(Document):
    meta = {"collection": "noc.eventclasscategories", "strict": False, "auto_create_index": False}
    name = StringField()
    parent = ObjectIdField(required=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if " | " in self.name:
            p_name = " | ".join(self.name.split(" | ")[:-1])
            p = EventClassCategory.objects.filter(name=p_name).first()
            if not p:
                p = EventClassCategory(name=p_name)
                p.save()
            self.parent = p.id
        else:
            self.parent = None
        super().save(*args, **kwargs)


@bi_sync
@change
@on_delete_check(
    check=[
        ("fm.EventClassificationRule", "event_class"),
        ("fm.ArchivedEvent", "event_class"),
        ("fm.ActiveEvent", "event_class"),
    ]
)
class EventClass(Document):
    """
    Event class
    """

    meta = {
        "collection": "noc.eventclasses",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "fm.eventclasses",
        "json_depends_on": ["fm.alarmclasses"],
        "json_unique_fields": ["name"],
    }
    name = StringField(required=True, unique=True)
    uuid = UUIDField(binary=True)
    description = StringField(required=False)
    # Event processing action:
    #     D - Drop
    #     L - Log as processed, do not move to archive
    #     A - Log as processed, move to archive
    action = StringField(
        required=True, choices=[("D", "Drop"), ("L", "Log"), ("A", "Log & Archive")]
    )
    vars: List[EventClassVar] = EmbeddedDocumentListField(EventClassVar)
    # Text messages
    subject_template = StringField()
    body_template = StringField()
    symptoms = StringField()
    probable_causes = StringField()
    recommended_actions = StringField()

    disposition = ListField(EmbeddedDocumentField(EventDispositionRule))
    # Window to suppress duplicated events (in seconds)
    # 0 means no deduplication
    deduplication_window = IntField(default=3)
    # Window to suppress repeated events (in seconds)
    # 0 means no suppression
    suppression_window = IntField(default=0)
    # Time to live in active window, unless not belonging to any alarm
    # (in seconds)
    ttl = IntField(default=86400)
    # True if event processing is regulated by
    # Interface Profile.link_events setting
    link_event = BooleanField(default=False)
    #
    handlers = ListField(StringField())
    # Plugin settings
    plugins = ListField(EmbeddedDocumentField(EventPlugin))
    #
    bi_id = LongField(unique=True)
    #
    category = ObjectIdField()

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _handlers_cache = {}

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["EventClass"]:
        return EventClass.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name):
        return EventClass.objects.filter(name=name).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["EventClass"]:
        return EventClass.objects.filter(bi_id=bi_id).first()

    def get_handlers(self):
        @cachetools.cached(self._handlers_cache, key=lambda x: x.id, lock=handlers_lock)
        def _get_handlers(event_class):
            handlers = []
            for hh in event_class.handlers:
                try:
                    h = get_handler(hh)
                except ImportError:
                    h = None
                if h:
                    handlers += [h]
            return handlers

        return _get_handlers(self)

    def clean(self):
        try:
            jinja2.Template(self.subject_template)
        except jinja2.TemplateSyntaxError as e:
            raise ValidationError(f"Subject template error {e}")
        try:
            jinja2.Template(self.body_template)
        except jinja2.TemplateSyntaxError as e:
            raise ValidationError(f"Subject body error {e}")
        super().clean()

    def save(self, *args, **kwargs):
        c_name = " | ".join(self.name.split(" | ")[:-1])
        c = EventClassCategory.objects.filter(name=c_name).first()
        if not c:
            c = EventClassCategory(name=c_name)
            c.save()
        self.category = c.id
        super().save(*args, **kwargs)

    def iter_changed_datastream(self, changed_fields=None):
        if config.datastream.enable_cfgevent:
            yield "cfgevent", f"ec:{self.id}"

    @property
    def display_action(self):
        return {"D": "Drop", "L": "Log", "A": "Log and Archive"}[self.action]

    def to_json(self) -> str:
        c = self
        r = ["{"]
        r += ['    "name": "%s",' % q(c.name)]
        r += ['    "$collection": "%s",' % self._meta["json_collection"]]
        r += ['    "uuid": "%s",' % c.uuid]
        if c.description:
            r += ['    "description": "%s",' % q(c.description)]
        r += ['    "action": "%s",' % q(c.action)]
        # vars
        vars = []
        for v in c.vars:
            vd = ["        {"]
            vd += ['            "name": "%s",' % q(v.name)]
            vd += ['            "description": "%s",' % q(v.description)]
            vd += ['            "type": "%s",' % q(v.type.value)]
            vd += ['            "required": %s,' % q(v.required)]
            vd += ['            "match_suppress": %s' % q(v.required)]
            vd += ["        }"]
            vars += ["\n".join(vd)]
        r += ['    "vars": [']
        r += [",\n".join(vars)]
        r += ["    ],"]
        if self.link_event:
            r += ['    "link_event": true,']
        r += ['    "deduplication_window": %d,' % self.deduplication_window]
        r += ['    "suppression_window": %d,' % self.suppression_window]
        r += ['    "ttl": %d,' % self.ttl]
        # Handlers
        if self.handlers:
            hh = ['        "%s"' % h for h in self.handlers]
            r += ['    "handlers": [']
            r += [",\n\n".join(hh)]
            r += ["    ],"]
        # Text
        r += ['    "subject_template": "%s",' % q(c.subject_template)]
        r += ['    "body_template": "%s",' % q(c.body_template)]
        r += ['    "symptoms": "%s",' % q(c.symptoms)]
        r += ['    "probable_causes": "%s",' % q(c.probable_causes)]
        r += ['    "recommended_actions": "%s",' % q(c.recommended_actions)]
        # Disposition rules
        if c.disposition:
            r += ['    "disposition": [']
            disp = []
            for d in c.disposition:
                ll = ["        {"]
                lll = ['            "name": "%s"' % q(d.name)]
                lll += ['            "condition": "%s"' % q(d.condition)]
                lll += ['            "action": "%s"' % q(d.action)]
                if d.alarm_class:
                    lll += ['            "alarm_class__name": "%s"' % q(d.alarm_class.name)]
                lll += ['            "stop_disposition": "%s"' % q(d.stop_disposition)]
                if d.managed_object:
                    lll += ['            "managed_object": "%s"' % q(d.managed_object)]
                ll += [",\n".join(lll)]
                ll += ["        }"]
                disp += ["\n".join(ll)]
            r += [",\n".join(disp)]
            r += ["    ]"]
            #
            if not r[-1].endswith(","):
                r[-1] += ","
        # Plugins
        if self.plugins:
            if not r[-1].endswith(","):
                r[-1] += ","
            plugins = []
            for p in self.plugins:
                pd = ["        {"]
                pd += ['            "name": "%s"' % p.name]
                if p.config:
                    pd[-1] += ","
                    pc = []
                    for v in p.config:
                        pc += ['                "%s": "%s"' % (v, p.config.vars[v])]
                    pd += ['            "config": {']
                    pd += [",\n".join(pc)]
                    pd += ["            }"]
                pd += ["        }"]
                plugins += ["\n".join(pd)]
            r += ['    "plugins": [']
            r += [",\n".join(plugins)]
            r += ["    ]"]
        # Close
        if r[-1].endswith(","):
            r[-1] = r[-1][:-1]
        r += ["}", ""]
        return "\n".join(r)

    def get_json_path(self) -> str:
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"

    @classmethod
    def get_event_config(cls, event_class: "EventClass"):
        """Build Category Rules"""
        from noc.fm.models.dispositionrule import DispositionRule

        r = {
            "id": str(event_class.id),
            "name": event_class.name,
            "bi_id": str(event_class.bi_id),
            "is_unique": True,
            "managed_object_required": True,
            "event_class": {
                "name": event_class.name,
                "id": str(event_class.id),
                "bi_id": str(event_class.bi_id),
            },
            "vars": [],
            "filters": [],
            "object_map": {
                "scope": "M",
                "managed_object_required": True,
                "include_path": True,
            },
            "handlers": [],
            "resources": [],
            "actions": [],
        }
        if event_class.deduplication_window:
            r["filters"].append(
                {"name": "dedup", "window": event_class.deduplication_window},
            )
        if event_class.suppression_window:
            r["filters"].append(
                {"name": "suppress", "window": event_class.suppression_window},
            )
        if event_class.link_event:
            r["resources"].append({"resource": "if"})
            if "noc.fm.handlers.event.link.oper_down" in event_class.handlers:
                r["resources"][-1]["oper_status"] = False
            elif "noc.fm.handlers.event.link.oper_up" in event_class.handlers:
                r["resources"][-1]["oper_status"] = True
        for vv in event_class.vars:
            r["vars"].append(
                {
                    "name": vv.name,
                    "type": vv.type.value,
                    "required": vv.required,
                    "match_suppress": vv.match_suppress,
                }
            )
        r["actions"] += DispositionRule.get_actions(event_class=event_class)
        if len(event_class.disposition) > 0:
            r["actions"] = [
                {
                    "name": event_class.name,
                    "is_active": True,
                    "preference": 99999,
                    "stop_processing": False,
                    "match_expr": [],
                    "event_classes": [],
                    "action": 3,
                }
            ]
        return r


rx_rule_name_quote = re.compile("[^a-zA-Z0-9]+")


def rulename_quote(s):
    """
    Convert arbitrary string to pyrule name

    >>> rulename_quote("Unknown | Default")
    'Unknown_Default'
    """
    return rx_rule_name_quote.sub("_", s)
