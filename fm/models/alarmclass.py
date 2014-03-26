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
        r += ["}", ""]
        return "\n".join(r)

    def get_json_path(self):
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"
