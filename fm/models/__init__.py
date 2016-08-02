# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## FM module database models
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import re
## Django modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
## NOC modules
from error import (MIBRequiredException, MIBNotFoundException,
                   InvalidTypedef, OIDCollision)
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.main.models import TimePattern, NotificationGroup, PyRule
from noc.main.models.template import Template as NOCTemplate

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
from eventclassificationrule import (
    EventClassificationRuleVar, EventClassificationPattern,
    EventClassificationRuleCategory, EventClassificationRule)


from cloneclassificationrule import CloneClassificationRule
from ignorepattern import IgnorePattern

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



from enumeration import Enumeration

##
## Event/Alarm text decoder
##
from utils import get_alarm, get_event


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
