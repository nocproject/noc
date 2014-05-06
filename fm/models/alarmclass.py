# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlarmClass model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import hashlib
import os
## Third-party modules
from mongoengine import fields
## NOC modules
import noc.lib.nosql as nosql
from alarmseverity import AlarmSeverity
from alarmclassvar import AlarmClassVar
from datasource import DataSource
from alarmrootcausecondition import AlarmRootCauseCondition
from alarmclasscategory import AlarmClassCategory
from alarmclassjob import AlarmClassJob
from alarmplugin import AlarmPlugin
from noc.lib.escape import json_escape as q
from noc.lib.text import quote_safe_path


class AlarmClass(nosql.Document):
    """
    Alarm class
    """
    meta = {
        "collection": "noc.alarmclasses",
        "allow_inheritance": False,
        "json_collection": "fm.alarmclasses"
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
    # alarm_class.text -> locale -> {
    #     "subject_template" -> <template>
    #     "body_template" -> <template>
    #     "symptoms" -> <text>
    #     "probable_causes" -> <text>
    #     "recommended_actions" -> <text>
    # }
    text = fields.DictField(required=True)
    # Flap detection
    flap_condition = fields.StringField(
        required=False,
        choices=[("none", "none"), ("count", "count")],
        default=None)
    flap_window = fields.IntField(required=False, default=0)
    flap_threshold = fields.FloatField(required=False, default=0)
    # RCA
    root_cause = fields.ListField(
        fields.EmbeddedDocumentField(AlarmRootCauseCondition))
    # Job descriptions
    jobs = fields.ListField(fields.EmbeddedDocumentField(AlarmClassJob))
    #
    handlers = fields.ListField(fields.StringField())
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
    #
    category = nosql.ObjectIdField()

    def __unicode__(self):
        return self.name

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
                x += ["            \"search\": {\n%s\n                }" % (",\n".join(ss))]
                jds += ["        {\n%s\n            }" % ",\n".join(x)]
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
        # text
        r += ["    \"text\": {"]
        t = []
        for lang in c.text:
            l = ["        \"%s\": {" % lang]
            ll = []
            for v in ["subject_template", "body_template", "symptoms",
                      "probable_causes", "recommended_actions"]:
                if v in c.text[lang]:
                    ll += ["            \"%s\": \"%s\"" % (v, q(c.text[lang][v]))]
            l += [",\n".join(ll)]
            l += ["        }"]
            t += ["\n".join(l)]
        r += [",\n\n".join(t)]
        r += ["    }"]
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
            r[-1] += ","
            r += ["    \"root_cause\": ["]
            r += [",\n".join(rc)]
            r += ["    ]"]
        # Jobs
        if self.jobs:
            jobs = []
            for job in self.jobs:
                jd = ["        {"]
                jd += ["            \"job\": \"%s\"," % job.job]
                jd += ["            \"interval\": %d," % job.interval]
                jd += ["            \"vars\": {"]
                jv = []
                for v in job.vars:
                    jv += ["                \"%s\": \"%s\"" % (v, job.vars[v])]
                jd += [",\n".join(jv)]
                jd += ["            }"]
                jd += ["        }"]
                jobs += ["\n".join(jd)]
            r[-1] += ","
            r += ["    \"jobs\": ["]
            r += [",\n".join(jobs)]
            r += ["    ]"]
        # Plugins
        if self.plugins:
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
            r[-1] += ","
            r += ["    \"notification_delay\": %d" % self.notification_delay]
        if self.control_time0:
            r[-1] += ","
            r += ["    \"control_time0\": %d" % self.control_time0]
            if self.control_time1:
                r[-1] += ","
                r += ["    \"control_time1\": %d" % self.control_time1]
                if self.control_timeN:
                    r[-1] += ","
                    r += ["    \"control_timeN\": %d" % self.control_timeN]
        # Close
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

## Avoid circular references
from alarmclassconfig import AlarmClassConfig