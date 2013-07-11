# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlarmClass model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import hashlib
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


class AlarmClass(nosql.Document):
    """
    Alarm class
    """
    meta = {
        "collection": "noc.alarmclasses",
        "allow_inheritance": False
    }

    name = fields.StringField(required=True, unique=True)
    is_builtin = fields.BooleanField(default=False)
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

    @property
    def json(self):
        c = self
        r = ["["]
        r += ["    {"]
        r += ["        \"name\": \"%s\"," % q(c.name)]
        r += ["        \"desciption\": \"%s\"," % q(c.description)]
        r += ["        \"is_unique\": %s," % q(c.is_unique)]
        if c.is_unique and c.discriminator:
            r += ["        \"discriminator\": [%s]," % ", ".join(["\"%s\"" % q(d) for d in c.discriminator])]
        r += ["        \"user_clearable\": %s," % q(c.user_clearable)]
        r += ["        \"default_severity__name\": \"%s\"," % q(c.default_severity.name)]
        # datasources
        if c.datasources:
            r += ["        \"datasources\": ["]
            jds = []
            for ds in c.datasources:
                x = []
                x += ["                \"name\": \"%s\"" % q(ds.name)]
                x += ["                \"datasource\": \"%s\"" % q(ds.datasource)]
                ss = []
                for k in sorted(ds.search):
                    ss += ["                    \"%s\": \"%s\"" % (q(k), q(ds.search[k]))]
                x += ["                \"search\": {\n%s\n                }" % (",\n".join(ss))]
                jds += ["            {\n%s\n            }" % ",\n".join(x)]
            r += [",\n\n".join(jds)]
            r += ["        ]"]
        # vars
        vars = []
        for v in c.vars:
            vd = ["            {"]
            vd += ["                \"name\": \"%s\"," % q(v.name)]
            vd += ["                \"description\": \"%s\"" % q(v.description)]
            if v.default:
                vd += ["                \"default\": \"%s\"" % q(v.default)]
            vd += ["            }"]
            vars += ["\n".join(vd)]
        r += ["        \"vars \": ["]
        r += [",\n\n".join(vars)]
        r += ["        ],"]
        # text
        r += ["        \"text\": {"]
        t = []
        for lang in c.text:
            l = ["            \"%s\": {" % lang]
            ll = []
            for v in ["subject_template", "body_template", "symptoms",
                      "probable_causes", "recommended_actions"]:
                if v in c.text[lang]:
                    ll += ["                \"%s\": \"%s\"" % (v, q(c.text[lang][v]))]
            l += [",\n".join(ll)]
            l += ["            }"]
            t += ["\n".join(l)]
        r += [",\n\n".join(t)]
        r += ["        }"]
        r += ["    }"]
        r += ["]"]
        return "\n".join(r)
