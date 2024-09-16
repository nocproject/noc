# ---------------------------------------------------------------------
# AlarmClass model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
from threading import Lock
import operator
from typing import Any, Dict, Optional, List, Callable, Union

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document
from mongoengine.document import EmbeddedDocument
from mongoengine.fields import (
    StringField,
    UUIDField,
    EmbeddedDocumentField,
    BooleanField,
    ListField,
    IntField,
    FloatField,
    LongField,
    ObjectIdField,
)
from mongoengine.errors import ValidationError
import cachetools
import jinja2

# NOC modules
from noc.core.text import quote_safe_path
from noc.core.handler import get_handler
from noc.core.bi.decorator import bi_sync
from noc.core.model.decorator import on_delete_check
from noc.core.change.decorator import change
from noc.core.prettyjson import to_json
from .datasource import DataSource
from .alarmrootcausecondition import AlarmRootCauseCondition
from .alarmclasscategory import AlarmClassCategory
from .alarmplugin import AlarmPlugin
from .alarmseverity import AlarmSeverity

id_lock = Lock()
handlers_lock = Lock()


class ComponentArgs(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

    param = StringField(required=True)
    var = StringField(required=True)


class Component(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

    name = StringField(required=True)
    model = StringField(required=True)
    args = ListField(EmbeddedDocumentField(ComponentArgs))

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name and self.model == other.model and self.args == other.args

    @property
    def json_data(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "model": self.model,
            "args": [{"param": a["param"], "var": a["var"]} for a in self.args],
        }


class AlarmClassVar(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    name = StringField(required=True)
    description = StringField(required=False)
    default_labels = ListField(StringField())
    default = StringField(required=False)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return (
            self.name == other.name
            and self.description == other.description
            and self.default == other.default
            and set(self.default_labels) == set(other.default_labels)
        )

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {"name": self.name, "description": self.description}
        if self.default:
            r["default"] = self.default
        if self.default_labels:
            r["default_labels"] = self.default_labels
        return r


@bi_sync
@change
@on_delete_check(
    check=[
        ("fm.ActiveAlarm", "alarm_class"),
        ("fm.AlarmClassConfig", "alarm_class"),
        ("fm.ArchivedAlarm", "alarm_class"),
        ("fm.AlarmDiagnosticConfig", "alarm_class"),
        ("sa.ObjectDiagnosticConfig", "alarm_class"),
        ("fm.EventClass", "disposition.alarm_class"),
        ("fm.AlarmRule", "groups.alarm_class"),
        ("fm.AlarmRule", "match.alarm_class"),
        ("fm.AlarmRule", "actions.alarm_class"),
    ]
)
class AlarmClass(Document):
    """
    Alarm class
    """

    meta = {
        "collection": "noc.alarmclasses",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "fm.alarmclasses",
        "json_depends_on": ["fm.alarmseverities"],
        "json_unique_fields": ["name"],
    }

    name = StringField(required=True, unique=True)
    uuid = UUIDField(binary=True)
    description = StringField(required=False)
    # if is_unique is True and there is active alarm
    # Do not create separate alarm if is_unique set
    is_unique = BooleanField(default=False)
    # Do not move alarm to Archive when clear, just delete
    is_ephemeral = BooleanField(default=False)
    # List of var names to be used as default reference key
    reference = ListField(StringField())
    # Can alarm status be cleared by user
    user_clearable = BooleanField(default=True)
    #
    datasources = ListField(EmbeddedDocumentField(DataSource))
    #
    components = ListField(EmbeddedDocumentField(Component))
    #
    vars = ListField(EmbeddedDocumentField(AlarmClassVar))
    # Text messages
    subject_template = StringField()
    body_template = StringField()
    symptoms = StringField()
    probable_causes = StringField()
    recommended_actions = StringField()

    # Flap detection
    flap_condition = StringField(
        required=False, choices=[("none", "none"), ("count", "count")], default="none"
    )
    flap_window = IntField(required=False, default=0)
    flap_threshold = FloatField(required=False, default=0)
    # RCA
    root_cause = ListField(EmbeddedDocumentField(AlarmRootCauseCondition))
    topology_rca = BooleanField(default=False)
    affected_service = BooleanField(default=False)
    # List of handlers to be called on alarm raising
    handlers = ListField(StringField())
    # List of handlers to be called on alarm clear
    clear_handlers = ListField(StringField())
    # Plugin settings
    plugins = ListField(EmbeddedDocumentField(AlarmPlugin))
    # Time in seconds to delay alarm risen notification
    notification_delay = IntField(required=False)
    # Control time to reopen alarm instead of creating new
    control_time0 = IntField(required=False)
    # Control time to reopen alarm after 1 reopen
    control_time1 = IntField(required=False)
    # Control time to reopen alarm after >1 reopen
    control_timeN = IntField(required=False)
    # Consequence recover time
    # Root cause will be detached if consequence alarm
    # will not clear itself in *recover_time*
    recover_time = IntField(required=False, default=300)
    #
    labels = ListField(StringField())
    #
    bi_id = LongField(unique=True)
    #
    category = ObjectIdField()

    _id_cache = cachetools.TTLCache(maxsize=1000, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=1000, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=1000, ttl=60)

    _handlers_cache = {}
    _clear_handlers_cache = {}

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["AlarmClass"]:
        return AlarmClass.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["AlarmClass"]:
        return AlarmClass.objects.filter(bi_id=bi_id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name: str) -> Optional["AlarmClass"]:
        return AlarmClass.objects.filter(name=name).first()

    @property
    def severity(self) -> Optional[AlarmSeverity]:
        if self.labels and self.labels[0].startswith("noc::severity::"):
            return AlarmSeverity.get_by_code(self.labels[0][15:].upper())
        return None

    def get_handlers(self) -> List[Callable]:
        @cachetools.cached(self._handlers_cache, key=lambda x: x.id, lock=handlers_lock)
        def _get_handlers(alarm_class: AlarmClass):
            handlers = []
            for hh in alarm_class.handlers:
                try:
                    h = get_handler(hh)
                except (ImportError, KeyError):  # Key error for cache exception
                    h = None
                if h:
                    handlers += [h]
            return handlers

        return _get_handlers(self)

    def get_clear_handlers(self):
        @cachetools.cached(self._clear_handlers_cache, key=lambda x: x.id, lock=handlers_lock)
        def _get_handlers(alarm_class: AlarmClass) -> List[Callable]:
            handlers = []
            for hh in alarm_class.clear_handlers:
                try:
                    h = get_handler(hh)
                except (ImportError, KeyError):  # Key error for cache exception
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
        c = AlarmClassCategory.objects.filter(name=c_name).first()
        if not c:
            c = AlarmClassCategory(name=c_name)
            c.save()
        self.category = c.id
        super().save(*args, **kwargs)

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "is_unique": self.is_unique,
            "is_ephemeral": self.is_ephemeral,
            "reference": [d for d in self.reference],
            "user_clearable": self.user_clearable,
            "labels": self.labels,
        }
        if self.description:
            r["description"] = self.description
        if self.datasources:
            r["datasources"] = [s.json_data for s in self.datasources]
        if self.components:
            r["components"] = [c.json_data for c in self.components]
        r["vars"] = [v.json_data for v in self.vars]
        if self.handlers:
            r["handlers"] = [h for h in self.handlers]
        if self.clear_handlers:
            r["clear_handlers"] = [h for h in self.clear_handlers]
        r["subject_template"] = self.subject_template
        r["body_template"] = self.body_template or ""
        r["symptoms"] = self.symptoms or ""
        r["probable_causes"] = self.probable_causes or ""
        r["recommended_actions"] = self.recommended_actions or ""
        if self.root_cause:
            r["root_cause"] = [rr.json_data for rr in self.root_cause]
        if self.topology_rca:
            r["topology_rca"] = True
        if self.affected_service:
            r["affected_service"] = self.affected_service
        if self.plugins:
            r["plugins"] = [p.json_data for p in self.plugins]
        if self.notification_delay:
            r["notification_delay"] = self.notification_delay
        if self.control_time0:
            r["control_time0"] = self.control_time0
            if self.control_time1:
                r["control_time1"] = self.control_time1
                if self.control_timeN:
                    r["control_timeN"] = self.control_timeN
        if self.recover_time:
            r["recover_time"] = self.recover_time
        return r

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=[
                "name",
                "$collection",
                "uuid",
                "description",
                "is_unique",
                "reference",
                "is_ephemeral",
                "user_clearable",
                "datasources",
                "components",
                "vars",
                "vars__interface",
                "vars__number",
                "handlers",
                "clear_handlers",
                "subject_template",
                "body_template",
                "symptoms",
                "probable_causes",
                "recommended_actions",
                "root_cause",
                "topology_rca",
                "affected_service",
                "plugins",
                "notification_delay",
                "control_time0",
                "recover_time",
                "root__name",
                "window",
                "condition",
                "match_condition",
                "model",
            ],
        )

    def get_json_path(self) -> str:
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"

    @property
    def config(self):
        if not hasattr(self, "_config"):
            self._config = AlarmClassConfig.objects.filter(alarm_class=self.id).first()
        return self._config

    def get_notification_delay(self):
        if self.config:
            return self.config.notification_delay or None
        else:
            return self.notification_delay or None

    def get_control_time(self, reopens: int) -> Optional[int]:
        if reopens == 0:
            if self.config:
                return self.config.control_time0 or None
            else:
                return self.control_time0 or None
        elif reopens == 1:
            if self.config:
                return self.config.control_time1 or None
            else:
                return self.control_time1 or None
        elif self.config:
            return self.config.control_timeN or None
        else:
            return self.control_timeN or None

    def get_labels_map(self):
        """
        Convert vars with default_labels to Map Label Scope -> Var Name
        :return:
        """
        if hasattr(self, "_var_labels_map"):
            return self._var_labels_map
        self._var_labels_map = {}
        for vv in self.vars:
            if not vv.default_labels:
                continue
            for ll in vv.default_labels:
                self._var_labels_map[ll.rstrip(":*")] = vv.name
        return self._var_labels_map

    def convert_labels_var(self, labels: List[str]) -> Dict[str, str]:
        """
        Convert labels to dict
        :param labels:
        :return:
        """
        r = {}
        var_labels_map = self.get_labels_map()
        for ll in labels:
            scope, *values = ll.rsplit("::", 1)
            if not values or scope not in var_labels_map:
                continue
            r[var_labels_map[scope]] = values[0]
        return r


# Avoid circular references
from .alarmclassconfig import AlarmClassConfig
