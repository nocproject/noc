# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# AlarmClass model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import hashlib
import os
from threading import Lock
import operator

# Third-party modules
import six
from mongoengine.document import Document
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
import cachetools

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from noc.core.escape import json_escape as q
from noc.core.text import quote_safe_path
from noc.core.handler import get_handler
from noc.core.bi.decorator import bi_sync
from noc.core.model.decorator import on_delete_check
from noc.core.comp import smart_bytes
from .alarmseverity import AlarmSeverity
from .alarmclassvar import AlarmClassVar
from .datasource import DataSource
from .alarmrootcausecondition import AlarmRootCauseCondition
from .alarmclasscategory import AlarmClassCategory
from .alarmplugin import AlarmPlugin

id_lock = Lock()
handlers_lock = Lock()


@bi_sync
@on_delete_check(
    check=[
        ("fm.ActiveAlarm", "alarm_class"),
        ("fm.AlarmClassConfig", "alarm_class"),
        ("fm.ArchivedAlarm", "alarm_class"),
    ]
)
@six.python_2_unicode_compatible
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
    # Create or not create separate Alarm
    # if is_unique is True and there is active alarm
    # Do not create separate alarm if is_unique set
    is_unique = BooleanField(default=False)
    # List of var names to be used as discriminator key
    discriminator = ListField(StringField())
    # Can alarm status be cleared by user
    user_clearable = BooleanField(default=True)
    # Default alarm severity
    default_severity = PlainReferenceField(AlarmSeverity)
    #
    datasources = ListField(EmbeddedDocumentField(DataSource))
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
    def get_by_id(cls, id):
        return AlarmClass.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, id):
        return AlarmClass.objects.filter(bi_id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name):
        return AlarmClass.objects.filter(name=name).first()

    def get_handlers(self):
        @cachetools.cached(self._handlers_cache, key=lambda x: x.id, lock=handlers_lock)
        def _get_handlers(alarm_class):
            handlers = []
            for hh in alarm_class.handlers:
                try:
                    h = get_handler(hh)
                except ImportError:
                    h = None
                if h:
                    handlers += [h]
            return handlers

        return _get_handlers(self)

    def get_clear_handlers(self):
        @cachetools.cached(self._clear_handlers_cache, key=lambda x: x.id, lock=handlers_lock)
        def _get_handlers(alarm_class):
            handlers = []
            for hh in alarm_class.clear_handlers:
                try:
                    h = get_handler(hh)
                except ImportError:
                    h = None
                if h:
                    handlers += [h]
            return handlers

        return _get_handlers(self)

    def save(self, *args, **kwargs):
        c_name = " | ".join(self.name.split(" | ")[:-1])
        c = AlarmClassCategory.objects.filter(name=c_name).first()
        if not c:
            c = AlarmClassCategory(name=c_name)
            c.save()
        self.category = c.id
        super(AlarmClass, self).save(*args, **kwargs)

    def get_discriminator(self, vars):
        """
        Calculate discriminator hash

        :param vars: Dict of vars
        :returns: Discriminator hash
        """
        if vars:
            ds = sorted(str(vars[n]) for n in self.discriminator)
            return hashlib.sha1(smart_bytes("\x00".join(ds))).hexdigest()
        return hashlib.sha1(b"").hexdigest()

    def to_json(self):
        c = self
        r = ["{"]
        r += ['    "name": "%s",' % q(c.name)]
        r += ['    "$collection": "%s",' % self._meta["json_collection"]]
        r += ['    "uuid": "%s",' % c.uuid]
        if c.description:
            r += ['    "desciption": "%s",' % q(c.description)]
        r += ['    "is_unique": %s,' % q(c.is_unique)]
        if c.is_unique and c.discriminator:
            r += [
                '    "discriminator": [%s],' % ", ".join(['"%s"' % q(d) for d in c.discriminator])
            ]
        r += ['    "user_clearable": %s,' % q(c.user_clearable)]
        r += ['    "default_severity__name": "%s",' % q(c.default_severity.name)]
        # datasources
        if c.datasources:
            r += ['    "datasources": [']
            jds = []
            for ds in c.datasources:
                x = []
                x += ['            "name": "%s"' % q(ds.name)]
                x += ['            "datasource": "%s"' % q(ds.datasource)]
                ss = []
                for k in sorted(ds.search):
                    ss += ['                "%s": "%s"' % (q(k), q(ds.search[k]))]
                x += ['            "search": {\n%s\n            }' % (",\n".join(ss))]
                jds += ["        {\n%s\n        }" % ",\n".join(x)]
            r += [",\n\n".join(jds)]
            r += ["    ],"]
        # vars
        vars = []
        for v in c.vars:
            vd = ["        {"]
            vd += ['            "name": "%s",' % q(v.name)]
            vd += ['            "description": "%s"' % q(v.description)]
            if v.default:
                vd[-1] += ","
                vd += ['            "default": "%s"' % q(v.default)]
            vd += ["        }"]
            vars += ["\n".join(vd)]
        r += ['    "vars": [']
        r += [",\n".join(vars)]
        r += ["    ],"]
        # Handlers
        if self.handlers:
            hh = ['        "%s"' % h for h in self.handlers]
            r += ['    "handlers": [']
            r += [",\n\n".join(hh)]
            r += ["    ],"]
        if self.clear_handlers:
            hh = ['        "%s"' % h for h in self.clear_handlers]
            r += ['    "clear_handlers": [']
            r += [",\n\n".join(hh)]
            r += ["    ],"]
        # Text
        r += ['    "subject_template": "%s",' % q(c.subject_template)]
        r += ['    "body_template": "%s",' % q(c.body_template)]
        r += ['    "symptoms": "%s",' % q(c.symptoms if c.symptoms else "")]
        r += ['    "probable_causes": "%s",' % q(c.probable_causes if c.probable_causes else "")]
        r += [
            '    "recommended_actions": "%s",'
            % q(c.recommended_actions if c.recommended_actions else "")
        ]
        # Root cause
        if self.root_cause:
            rc = []
            for rr in self.root_cause:
                rcd = ["        {"]
                rcd += ['            "name": "%s",' % rr.name]
                rcd += ['            "root__name": "%s",' % rr.root.name]
                rcd += ['            "window": %d,' % rr.window]
                if rr.condition:
                    rcd += ['            "condition": "%s",' % rr.condition]
                rcd += ['            "match_condition": {']
                mcv = []
                for v in rr.match_condition:
                    mcv += ['                "%s": "%s"' % (v, rr.match_condition[v])]
                rcd += [",\n".join(mcv)]
                rcd += ["            }"]
                rcd += ["        }"]
                rc += ["\n".join(rcd)]
            if r[-1][-1] != ",":
                r[-1] += ","
            r += ['    "root_cause": [']
            r += [",\n".join(rc)]
            r += ["    ]"]
        if self.topology_rca:
            if r[-1][-1] != ",":
                r[-1] += ","
            r += ['    "topology_rca": true']
        # Plugins
        if self.plugins:
            if r[-1][-1] != ",":
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
        if self.notification_delay:
            if r[-1][-1] != ",":
                r[-1] += ","
            r += ['    "notification_delay": %d' % self.notification_delay]
        if self.control_time0:
            if r[-1][-1] != ",":
                r[-1] += ","
            r += ['    "control_time0": %d' % self.control_time0]
            if self.control_time1:
                r[-1] += ","
                r += ['    "control_time1": %d' % self.control_time1]
                if self.control_timeN:
                    r[-1] += ","
                    r += ['    "control_timeN": %d' % self.control_timeN]
        if self.recover_time:
            if r[-1][-1] != ",":
                r[-1] += ","
            r += ['    "recover_time": %d' % self.recover_time]
        # Close
        if r[-1].endswith(","):
            r[-1] = r[-1][:-1]
        r += ["}", ""]
        return "\n".join(r)

    def get_json_path(self):
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

    def get_control_time(self, reopens):
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
        else:
            if self.config:
                return self.config.control_timeN or None
            else:
                return self.control_timeN or None


# Avoid circular references
from .alarmclassconfig import AlarmClassConfig
