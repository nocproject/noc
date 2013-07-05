# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EventClass model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## Third-party modules
from mongoengine import fields
from mongoengine.document import EmbeddedDocument, Document
## NOC modules
from noc.lib import nosql
from alarmclass import AlarmClass
from noc.lib.escape import json_escape as q


class EventClassVar(EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }
    name = fields.StringField(required=True)
    description = fields.StringField(required=False)
    type = fields.StringField(
        required=True,
        choices=[
            (x, x) for x in (
                "str", "int",
                "ipv4_address", "ipv6_address", "ip_address",
                "ipv4_prefix", "ipv6_prefix", "ip_prefix",
                "mac", "interface_name", "oid"
            )]
    )
    required = fields.BooleanField(required=True)

    def __unicode__(self):
        return self.name

    def __eq__(self, other):
        return (self.name == other.name and
                self.description == other.description and
                self.type == other.type and
                self.required == other.required)


class EventDispositionRule(EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }
    # Name, unique within event class
    name = fields.StringField(required=True, default="dispose")
    # Python logical expression to check do the rules
    # applicable or not.
    condition = fields.StringField(required=True, default="True")
    # What to do with disposed event:
    #    drop - delete and stop disposition
    #    ignore - stop disposition
    #    pyrule - execute pyrule
    #    raise - raise an alarm
    #    clear - clear alarm
    #
    action = fields.StringField(
        required=True,
        choices=[(x, x) for x in (
            "drop",
            "ignore",
            "raise",
            "clear"
        )]
    )
    # Applicable for actions: raise and clear
    alarm_class = nosql.PlainReferenceField(AlarmClass, required=False)
    # Additional condition. Raise or clear action
    # will be performed only if additional events occured during time window
    combo_condition = fields.StringField(
        required=False,
        default="none",
        choices=[(x, x) for x in (
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
            "any"
        )]
    )
    # Time window for combo events in seconds
    combo_window = fields.IntField(required=False, default=0)
    # Applicable for frequency.
    combo_count = fields.IntField(required=False, default=0)
    # Applicable for sequence, all and any combo_condition
    combo_event_classes = fields.ListField(
        nosql.PlainReferenceField("EventClass"),
        required=False,
        default=[])
    # event var name -> alarm var name mappings
    # try to use direct mapping if not set explicitly
    var_mapping = fields.DictField(required=False)
    # Stop event disposition if True or continue with next rule
    stop_disposition = fields.BooleanField(required=False, default=True)

    def __unicode__(self):
        return "%s: %s" % (self.action, self.alarm_class.name)

    def __eq__(self, other):
        for a in ["name", "condition", "action", "pyrule", "window",
                  "var_mapping", "stop_disposition"]:
            if hasattr(self, a) != hasattr(other, a):
                return False
            if hasattr(self, a) and getattr(self, a) != getattr(other, a):
                return False
        if self.alarm_class is None and other.alarm_class is None:
            return True
        if (self.alarm_class is None or other.alarm_class is None or
                self.alarm_class.name != other.alarm_class.name):
            return False
        return True


class EventSuppressionRule(EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }
    name = fields.StringField()
    condition = fields.StringField(required=True, default="True")
    event_class = nosql.PlainReferenceField("EventClass", required=True)
    match_condition = fields.DictField(required=True, default={})
    window = fields.IntField(required=True, default=3600)
    suppress = fields.BooleanField(required=True, default=True)

    def __unicode__(self):
        return self.name

    def __eq__(self, other):
        return (
            self.name == other.name and
            self.condition == other.condition and
            self.event_class.id == other.event_class.id and
            self.match_condition == other.match_condition and
            self.window == other.window and
            self.suppress == other.suppress
        )


class EventPlugin(EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }

    name = fields.StringField()
    config = fields.DictField(default={})

    def __unicode__(self):
        return self.name


class EventClassCategory(nosql.Document):
    meta = {
        "collection": "noc.eventclasscategories",
        "allow_inheritance": False
    }
    name = fields.StringField()
    parent = fields.ObjectIdField(required=False)

    def __unicode__(self):
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
        super(EventClassCategory, self).save(*args, **kwargs)


class EventClass(Document):
    """
    Event class
    """
    meta = {
        "collection": "noc.eventclasses",
        "allow_inheritance": False
    }
    name = fields.StringField(required=True, unique=True)
    is_builtin = fields.BooleanField(default=False)
    description = fields.StringField(required=False)
    # Event processing action:
    #     D - Drop
    #     L - Log as processed, do not move to archive
    #     A - Log as processed, move to archive
    action = fields.StringField(
        required=True,
        choices=[
            ("D", "Drop"),
            ("L", "Log"),
            ("A", "Log & Archive")
        ]
    )
    vars = fields.ListField(fields.EmbeddedDocumentField(EventClassVar))
    # Text messages
    # alarm_class.text -> locale -> {
    #     "subject_template" -> <template>
    #     "body_template" -> <template>
    #     "symptoms" -> <text>
    #     "probable_causes" -> <text>
    #     "recommended_actions" -> <text>
    # }
    text = fields.DictField(required=True)

    disposition = fields.ListField(
        fields.EmbeddedDocumentField(EventDispositionRule))
    repeat_suppression = fields.ListField(
        fields.EmbeddedDocumentField(EventSuppressionRule))
    # True if event processing is regulated by
    # Interface Profile.link_events setting
    link_event = fields.BooleanField(default=False)
    # Plugin settings
    plugins = fields.ListField(fields.EmbeddedDocumentField(EventPlugin))
    #
    category = fields.ObjectIdField()

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        c_name = " | ".join(self.name.split(" | ")[:-1])
        c = EventClassCategory.objects.filter(name=c_name).first()
        if not c:
            c = EventClassCategory(name=c_name)
            c.save()
        self.category = c.id
        super(EventClass, self).save(*args, **kwargs)

    @property
    def display_action(self):
        return {
            "D": "Drop",
            "L": "Log",
            "A": "Log and Archive"
        }[self.action]

    @property
    def conditional_pyrule_name(self):
        return ("fm_dc_" + rulename_quote(self.name)).lower()

    @property
    def json(self):
        c = self
        r = ["["]
        r += ["    {"]
        r += ["        \"name\": \"%s\"," % q(c.name)]
        r += ["        \"desciption\": \"%s\"," % q(c.description)]
        r += ["        \"action\": \"%s\"," % q(c.action)]
        # vars
        vars = []
        for v in c.vars:
            vd = ["            {"]
            vd += ["                \"name\": \"%s\"," % q(v.name)]
            vd += ["                \"description\": \"%s\"," % q(v.description)]
            vd += ["                \"type\": \"%s\"," % q(v.type)]
            vd += ["                \"required\": %s," % q(v.required)]
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
        # Disposition rules
        if c.disposition:
            r += ["        },"]
            r += ["        \"disposition\": ["]
            l = []
            for d in c.disposition:
                ll = ["            {"]
                lll = ["                \"name\": \"%s\"" % q(d.name)]
                lll += ["                \"condition\": \"%s\"" % q(d.condition)]
                lll += ["                \"action\": \"%s\"" % q(d.action)]
                if d.alarm_class:
                    lll += ["                \"alarm_class__name\": \"%s\"" % q(d.alarm_class.name)]
                ll += [",\n".join(lll)]
                ll += ["            }"]
                l += ["\n".join(ll)]
            r += [",\n".join(l)]
            r += ["        ]"]
        r += ["    }"]
        r += ["]"]
        return "\n".join(r)

rx_rule_name_quote = re.compile("[^a-zA-Z0-9]+")


def rulename_quote(s):
    """
    Convert arbitrary string to pyrule name

    >>> rulename_quote("Unknown | Default")
    'Unknown_Default'
    """
    return rx_rule_name_quote.sub("_", s)
