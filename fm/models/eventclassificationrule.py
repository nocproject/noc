# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EventClassificationRule model
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## Third-party modules
from mongoengine import fields
from mongoengine.document import EmbeddedDocument, Document
## NOC modules
from eventclass import EventClass
from datasource import DataSource
from noc.lib.nosql import PlainReferenceField
from noc.lib.escape import json_escape as jq
from noc.lib.text import quote_safe_path


class EventClassificationRuleVar(EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }
    name = fields.StringField(required=True)
    value = fields.StringField(required=False)

    def __unicode__(self):
        return self.name

    def __eq__(self, other):
        return (self.name == other.name and
                self.value == other.value)


class EventClassificationRuleCategory(Document):
    meta = {
        "collection": "noc.eventclassificationrulecategories",
        "allow_inheritance": False
    }
    name = fields.StringField()
    parent = fields.ObjectIdField(required=False)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if " | " in self.name:
            p_name = " | ".join(self.name.split(" | ")[:-1])
            p = EventClassificationRuleCategory.objects.filter(name=p_name).first()
            if not p:
                p = EventClassificationRuleCategory(name=p_name)
                p.save()
            self.parent = p.id
        else:
            self.parent = None
        super(EventClassificationRuleCategory, self).save(*args, **kwargs)


class EventClassificationPattern(EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }
    key_re = fields.StringField(required=True)
    value_re = fields.StringField(required=True)

    def __unicode__(self):
        return u"'%s' : '%s'" % (self.key_re, self.value_re)

    def __eq__(self, other):
        return self.key_re == other.key_re and self.value_re == other.value_re


class EventClassificationRule(Document):
    """
    Classification rules
    """
    meta = {
        "collection": "noc.eventclassificationrules",
        "allow_inheritance": False,
        "json_collection": "fm.eventclassificationrules"
    }
    name = fields.StringField(required=True, unique=True)
    uuid = fields.UUIDField(binary=True)
    description = fields.StringField(required=False)
    event_class = PlainReferenceField(EventClass, required=True)
    preference = fields.IntField(required=True, default=1000)
    patterns = fields.ListField(fields.EmbeddedDocumentField(EventClassificationPattern))
    datasources = fields.ListField(fields.EmbeddedDocumentField(DataSource))
    vars = fields.ListField(fields.EmbeddedDocumentField(EventClassificationRuleVar))
    #
    category = fields.ObjectIdField()

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        c_name = " | ".join(self.name.split(" | ")[:-1])
        c = EventClassificationRuleCategory.objects.filter(name=c_name).first()
        if not c:
            c = EventClassificationRuleCategory(name=c_name)
            c.save()
        self.category = c.id
        super(EventClassificationRule, self).save(*args, **kwargs)

    @property
    def short_name(self):
        return self.name.split(" | ")[-1]

    def to_json(self):
        r = ["{"]
        r += ["    \"name\": \"%s\"," % jq(self.name)]
        r += ["    \"uuid\": \"%s\"," % self.uuid]
        if self.description:
            r += ["    \"description\": \"%s\"," % jq(self.description)]
        r += ["    \"event_class__name\": \"%s\"," % jq(self.event_class.name)]
        r += ["    \"preference\": %d," % self.preference]
        # Dump datasources
        if self.datasources:
            r += ["    \"datasources\": ["]
            jds = []
            for ds in self.datasources:
                x = ["        \"name\": \"%s\"" % jq(ds.name)]
                x += ["        \"datasource\": \"%s\"" % jq(ds.datasource)]
                ss = []
                for k in sorted(ds.search):
                    ss += ["            \"%s\": \"%s\"" % (jq(k), jq(ds.search[k]))]
                x += ["            \"search\": {"]
                x += [",\n".join(ss)]
                x += ["            }"]
                jds += ["        {", ",\n".join(x), "        }"]
            r += [",\n\n".join(jds)]
            r += ["    ],"]
        # Dump vars
        if self.vars:
            r += ["    \"vars\": ["]
            vars = []
            for v in self.vars:
                vd = ["        {"]
                vd += ["            \"name\": \"%s\"" % jq(v.name)]
                vd += ["            \"value\": \"%s\"" % jq(v.value)]
                vd += ["        }"]
                vars += ["\n".join(vd)]
            r += [",\n\n".join(vars)]
            r += ["    ],"]
        # Dump patterns
        r += ["    \"patterns\": ["]
        patterns = []
        for p in self.patterns:
            pt = []
            pt += ["        {"]
            pt += ["            \"key_re\": \"%s\"," % jq(p.key_re)]
            pt += ["            \"value_re\": \"%s\"" % jq(p.value_re)]
            pt += ["        }"]
            patterns += ["\n".join(pt)]
        r += [",\n".join(patterns)]
        r += ["    ]"]
        r += ["}"]
        return "\n".join(r)

    def get_json_path(self):
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"
