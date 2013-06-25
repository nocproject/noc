# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## FM module database models
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import datetime
import re
## Django modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
## NOC modules
from error import (MIBRequiredException, MIBNotFoundException,
                   InvalidTypedef, OIDCollision)
from noc.sa.models import ManagedObject, ManagedObjectSelector
from noc.main.models import TimePattern, NotificationGroup, PyRule, Style, User
from noc.main.models import Template as NOCTemplate
import noc.lib.nosql as nosql
from noc.lib.escape import json_escape as jq


##
## Regular expressions
##
rx_py_id = re.compile("[^0-9a-zA-Z]+")
rx_mibentry = re.compile(r"^((\d+\.){5,}\d+)|(\S+::\S+)$")
rx_mib_name = re.compile(r"^(\S+::\S+?)(.\d+)?$")


##
## MIB Processing
##
from oidalias import OIDAlias
from syntaxalias import SyntaxAlias
from mibpreference import MIBPreference
from mib import MIB
from mibdata import MIBData
from mibalias import MIBAlias


##
## Alarms and Events
##
from alarmseverity import AlarmSeverity
from alarmclassvar import AlarmClassVar
from datasource import DataSource
from alarmrootcausecondition import AlarmRootCauseCondition
from alarmclassjob import AlarmClassJob
from alarmclasscategory import AlarmClassCategory
from alarmclass import AlarmClass
from eventclass import (EventClass, EventClassCategory, EventClassVar,
                        EventDispositionRule, EventSuppressionRule)


##
## Classification rules
##
class EventClassificationRuleVar(nosql.EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }
    name = nosql.StringField(required=True)
    value = nosql.StringField(required=False)

    def __unicode__(self):
        return self.name

    def __eq__(self, other):
        return (self.name == other.name and
                self.value == other.value)


class EventClassificationRuleCategory(nosql.Document):
    meta = {
        "collection": "noc.eventclassificationrulecategories",
        "allow_inheritance": False
    }
    name = nosql.StringField()
    parent = nosql.ObjectIdField(required=False)
    
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


class EventClassificationPattern(nosql.EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }
    key_re = nosql.StringField(required=True)
    value_re = nosql.StringField(required=True)
    
    def __unicode__(self):
        return u"'%s' : '%s'" % (self.key_re, self.value_re)

    def __eq__(self, other):
        return self.key_re == other.key_re and self.value_re == other.value_re


class EventClassificationRule(nosql.Document):
    """
    Classification rules
    """
    meta = {
        "collection": "noc.eventclassificationrules",
        "allow_inheritance": False
    }
    name = nosql.StringField(required=True, unique=True)
    is_builtin = nosql.BooleanField(required=True)
    description = nosql.StringField(required=False)
    event_class = nosql.PlainReferenceField(EventClass, required=True)
    preference = nosql.IntField(required=True, default=1000)
    patterns = nosql.ListField(nosql.EmbeddedDocumentField(EventClassificationPattern))
    datasources = nosql.ListField(nosql.EmbeddedDocumentField(DataSource))
    vars = nosql.ListField(nosql.EmbeddedDocumentField(EventClassificationRuleVar))
    #
    category = nosql.ObjectIdField()
    
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


class CloneClassificationRule(nosql.Document):
    """
    Classification rules cloning
    """
    meta = {
        "collection": "noc.cloneclassificationrules",
        "allow_inheritance": False
    }

    name = nosql.StringField(unique=True)
    re = nosql.StringField(default="^.*$")
    key_re = nosql.StringField(default="^.*$")
    value_re = nosql.StringField(default="^.*$")
    is_builtin = nosql.BooleanField(default=False)
    rewrite_from = nosql.StringField()
    rewrite_to = nosql.StringField()

    def __unicode__(self):
        return self.name

##
## Events.
## Events are divided to 4 statuses:
##     New
##     Active
##     Failed
##     Archived
##
EVENT_STATUS_NAME = {
    "N": "New",
    "F": "Failed",
    "A": "Active",
    "S": "Archived"
}

from eventlog import EventLog
from newevent import NewEvent
from failedevent import FailedEvent
from activeevent import ActiveEvent
from archivedevent import ArchivedEvent
from alarmlog import AlarmLog
from activealarm import ActiveAlarm
from archivedalarm import ArchivedAlarm


class IgnoreEventRules(models.Model):
    class Meta:
        verbose_name = "Ignore Event Rule"
        verbose_name_plural = "Ignore Event Rules"
        unique_together = [("left_re", "right_re")]

    name = models.CharField("Name", max_length=64, unique=True)
    left_re = models.CharField("Left RE", max_length=256)
    right_re = models.CharField("Right Re", max_length=256)
    is_active = models.BooleanField("Is Active", default=True)
    description = models.TextField("Description", null=True, blank=True)

    def __unicode__(self):
        return u"%s (%s, %s)" % (self.name, self.left_re, self.right_re)


class EventTrigger(models.Model):
    class Meta:
        verbose_name = _("Event Trigger")
        verbose_name_plural = _("Event Triggers")

    name = models.CharField(_("Name"), max_length=64, unique=True)
    is_enabled = models.BooleanField(_("Is Enabled"), default=True)
    event_class_re = models.CharField(_("Event class RE"), max_length=256)
    condition = models.CharField(_("Condition"), max_length=256, default="True")
    time_pattern = models.ForeignKey(TimePattern,
                                     verbose_name=_("Time Pattern"),
                                     null=True, blank=True)
    selector = models.ForeignKey(ManagedObjectSelector,
                                 verbose_name=_("Managed Object Selector"),
                                 null=True, blank=True)
    notification_group = models.ForeignKey(NotificationGroup,
                                           verbose_name=_("Notification Group"),
                                           null=True, blank=True)
    template = models.ForeignKey(NOCTemplate,
                                 verbose_name=_("Template"),
                                 null=True, blank=True)
    pyrule = models.ForeignKey(PyRule,
                               verbose_name=_("pyRule"),
                               null=True, blank=True,
                               limit_choices_to={"interface": "IEventTrigger"})
    
    def __unicode__(self):
        return "%s <<<%s>>>" % (self.event_class_re, self.condition)


class AlarmTrigger(models.Model):
    class Meta:
        verbose_name = _("Alarm Trigger")
        verbose_name_plural = _("Alarm Triggers")

    name = models.CharField(_("Name"), max_length=64, unique=True)
    is_enabled = models.BooleanField(_("Is Enabled"), default=True)
    alarm_class_re = models.CharField(_("Alarm class RE"), max_length=256)
    condition = models.CharField(_("Condition"), max_length=256, default="True")
    time_pattern = models.ForeignKey(TimePattern,
                                     verbose_name=_("Time Pattern"),
                                     null=True, blank=True)
    selector = models.ForeignKey(ManagedObjectSelector,
                                 verbose_name=_("Managed Object Selector"),
                                 null=True, blank=True)
    notification_group = models.ForeignKey(NotificationGroup,
                                           verbose_name=_("Notification Group"),
                                           null=True, blank=True)
    template = models.ForeignKey(NOCTemplate,
                                 verbose_name=_("Template"),
                                 null=True, blank=True)
    pyrule = models.ForeignKey(PyRule,
                               verbose_name=_("pyRule"),
                               null=True, blank=True,
                               limit_choices_to={"interface": "IAlarmTrigger"})
    
    def __unicode__(self):
        return "%s <<<%s>>>" % (self.alarm_class_re, self.condition)

from enumeration import Enumeration

##
## Event/Alarm text decoder
##
from translation import get_translated_template, get_translated_text


def get_event(event_id):
        """
        Get event by event_id
        """
        for ec in (ActiveEvent, ArchivedEvent, FailedEvent, NewEvent):
            e = ec.objects.filter(id=event_id).first()
            if e:
                return e
        return None


def get_alarm(alarm_id):
        """
        Get alarm by alarm_id
        """
        for ac in (ActiveAlarm, ArchivedAlarm):
            a = ac.objects.filter(id=alarm_id).first()
            if a:
                return a
        return None


def get_object_status(managed_object):
    """
    Returns current object status
    
    :param managed_object: Managed Object instance
    :returns: True, if object is up, False, if object is down, None, if object
              is unreachable
    """
    ac = AlarmClass.objects.get(name="NOC | Managed Object | Ping Failed")
    a = ActiveAlarm.objects.filter(managed_object=managed_object.id,
                                   alarm_class=ac.id).first()
    if a is None:
        # No active alarm, object is up
        return True
    elif a.root:
        # Inferred alarm, object status is unknown
        return None
    else:
        return False
