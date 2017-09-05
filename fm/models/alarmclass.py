# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# AlarmClass model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import hashlib
import os
from threading import Lock
import operator
# Third-party modules
from mongoengine import fields
import cachetools
# NOC modules
import noc.lib.nosql as nosql
from alarmseverity import AlarmSeverity
from alarmclassvar import AlarmClassVar
from datasource import DataSource
from alarmrootcausecondition import AlarmRootCauseCondition
from alarmclasscategory import AlarmClassCategory
from alarmplugin import AlarmPlugin
from noc.lib.escape import json_escape as q
from noc.lib.text import quote_safe_path
from noc.core.handler import get_handler

id_lock = Lock()
handlers_lock = Lock()


class AlarmClass(nosql.Document):
    """
    Alarm class
    """
    meta = {
        "collection": "noc.alarmclasses",
        "strict": False,
        "json_collection": "fm.alarmclasses",
        "json_depends_on": [
            "fm.alarmseverities"
        ],
    }

    name = fields.StringField(required=True, unique=True)
    uuid = fields.UUIDField(binary=True)
    description = fields.StringField(required=False)
    # Create or not create separate Alarm
    # if is_unique is True and there is active alarm
    # Do not create separate alarm if is_unique set
    is_unique = fields.BooleanField(default=False)
    # List of var names to be used as discriminator key
    discriminator = fields.ListField(nosql.StringField())
    # Can alarm status be cleared by user
    user_clearable = fields.BooleanField(default=True)
    # Default alarm severity
    default_severity = nosql.PlainReferenceField(AlarmSeverity)
    #
    datasources = fields.ListField(fields.EmbeddedDocumentField(DataSource))
    vars = fields.ListField(fields.EmbeddedDocumentField(AlarmClassVar))
    # Text messages
    subject_template = fields.StringField()
    body_template = fields.StringField()
    symptoms = fields.StringField()
    probable_causes = fields.StringField()
    recommended_actions = fields.StringField()

    # Flap detection
    flap_condition = fields.StringField(
        required=False,
        choices=[("none", "none"), ("count", "count")],
        default="none")
    flap_window = fields.IntField(required=False, default=0)
    flap_threshold = fields.FloatField(required=False, default=0)
    # RCA
    root_cause = fields.ListField(
        fields.EmbeddedDocumentField(AlarmRootCauseCondition))
    topology_rca = fields.BooleanField(default=False)
    # List of handlers to be called on alarm raising
    handlers = fields.ListField(fields.StringField())
    # List of handlers to be called on alarm clear
    clear_handlers = fields.ListField(fields.StringField())
    # Plugin settings
    plugins = fields.ListField(fields.EmbeddedDocumentField(AlarmPlugin))
    # Time in seconds to delay alarm risen notification
    notification_delay = fields.IntField(required=False)
    # Control time to reopen alarm instead of creating new
    control_time0 = fields.IntField(required=False)
    # Control time to reopen alarm after 1 reopen
    control_time1 = fields.IntField(required=False)
    # Control time to reopen alarm after >1 reopen
    control_timeN = fields.IntField(required=False)
    # Consequence recover time
    # Root cause will be detached if consequence alarm
    # will not clear itself in *recover_time*
    recover_time = fields.IntField(required=False, default=300)
    #
    category = nosql.ObjectIdField()

    _id_cache = cachetools.TTLCache(maxsize=1000, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=1000, ttl=60)

    _handlers_cache = {}
    _clear_handlers_cache = {}

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return AlarmClass.objects.filter(id=id).first()

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
            return hashlib.sha1("\x00".join(ds)).hexdigest()
        else:
            return hashlib.sha1("").hexdigest()

    def to_json(self):
        c = self
        r = ["{"]
        r += ["    \"name\": \"%s\"," % q(c.name)]
        r += ["    \"$collection\": \"%s\"," % self._meta["json_collection"]]
        r += ["    \"uuid\": \"%s\"," % c.uuid]
        if c.description:
            r += ["    \"desciption\": \"%s\"," % q(c.description)]
        r += ["    \"is_unique\": %s," % q(c.is_unique)]
        if c.is_unique and c.discriminator:
            r += ["    \"discriminator\": [%s]," % ", ".join(["\"%s\"" % q(d) for d in c.discriminator])]
        r += ["    \"user_clearable\": %s," % q(c.user_clearable)]
        r += ["    \"default_severity__name\": \"%s\"," % q(c.default_severity.name)]
        # datasources
        if c.datasources:
            r += ["    \"datasources\": ["]
            jds = []
            for ds in c.datasources:
                x = []
                x += ["            \"name\": \"%s\"" % q(ds.name)]
                x += ["            \"datasource\": \"%s\"" % q(ds.datasource)]
                ss = []
                for k in sorted(ds.search):
                    ss += ["                \"%s\": \"%s\"" % (q(k), q(ds.search[k]))]
                x += ["            \"search\": {\n%s\n            }" % (",\n".join(ss))]
                jds += ["        {\n%s\n        }" % ",\n".join(x)]
            r += [",\n\n".join(jds)]
            r += ["    ],"]
        # vars
        vars = []
        for v in c.vars:
            vd = ["        {"]
            vd += ["            \"name\": \"%s\"," % q(v.name)]
            vd += ["            \"description\": \"%s\"" % q(v.description)]
            if v.default:
                vd[-1] += ","
                vd += ["            \"default\": \"%s\"" % q(v.default)]
            vd += ["        }"]
            vars += ["\n".join(vd)]
        r += ["    \"vars\": ["]
        r += [",\n".join(vars)]
        r += ["    ],"]
        # Handlers
        if self.handlers:
            hh = ["        \"%s\"" % h for h in self.handlers]
            r += ["    \"handlers\": ["]
            r += [",\n\n".join(hh)]
            r += ["    ],"]
        if self.clear_handlers:
            hh = ["        \"%s\"" % h for h in self.clear_handlers]
            r += ["    \"clear_handlers\": ["]
            r += [",\n\n".join(hh)]
            r += ["    ],"]
        # Text
        r += ["    \"subject_template\": \"%s\"," % q(c.subject_template)]
        r += ["    \"body_template\": \"%s\"," % q(c.body_template)]
        r += ["    \"symptoms\": \"%s\"," % q(c.symptoms if c.symptoms else "")]
        r += ["    \"probable_causes\": \"%s\"," % q(c.probable_causes if c.probable_causes else "")]
        r += ["    \"recommended_actions\": \"%s\"," % q(c.recommended_actions if c.recommended_actions else "")]
        # Root cause
        if self.root_cause:
            rc = []
            for rr in self.root_cause:
                rcd = ["        {"]
                rcd += ["            \"name\": \"%s\"," % rr.name]
                rcd += ["            \"root__name\": \"%s\"," % rr.root.name]
                rcd += ["            \"window\": %d," % rr.window]
                if rr.condition:
                    rcd += ["            \"condition\": \"%s\"," % rr.condition]
                rcd += ["            \"match_condition\": {"]
                mcv = []
                for v in rr.match_condition:
                    mcv += ["                \"%s\": \"%s\"" % (v, rr.match_condition[v])]
                rcd += [",\n".join(mcv)]
                rcd += ["            }"]
                rcd += ["        }"]
                rc += ["\n".join(rcd)]
            if r[-1][-1] != ",":
                r[-1] += ","
            r += ["    \"root_cause\": ["]
            r += [",\n".join(rc)]
            r += ["    ]"]
        if self.topology_rca:
            if r[-1][-1] != ",":
                r[-1] += ","
            r += ["    \"topology_rca\": true"]
        # Plugins
        if self.plugins:
            if r[-1][-1] != ",":
                r[-1] += ","
            plugins = []
            for p in self.plugins:
                pd = ["        {"]
                pd += ["            \"name\": \"%s\"" % p.name]
                if p.config:
                    pd[-1] += ","
                    pc = []
                    for v in p.config:
                        pc += ["                \"%s\": \"%s\"" % (v, p.config.vars[v])]
                    pd += ["            \"config\": {"]
                    pd += [",\n".join(pc)]
                    pd += ["            }"]
                pd += ["        }"]
                plugins += ["\n".join(pd)]
            r += ["    \"plugins\": ["]
            r += [",\n".join(plugins)]
            r += ["    ]"]
        if self.notification_delay:
            if r[-1][-1] != ",":
                r[-1] += ","
            r += ["    \"notification_delay\": %d" % self.notification_delay]
        if self.control_time0:
            if r[-1][-1] != ",":
                r[-1] += ","
            r += ["    \"control_time0\": %d" % self.control_time0]
            if self.control_time1:
                r[-1] += ","
                r += ["    \"control_time1\": %d" % self.control_time1]
                if self.control_timeN:
                    r[-1] += ","
                    r += ["    \"control_timeN\": %d" % self.control_timeN]
        if self.recover_time:
            if r[-1][-1] != ",":
                r[-1] += ","
            r += ["    \"recover_time\": %d" % self.recover_time]
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
from alarmclassconfig import AlarmClassConfig
