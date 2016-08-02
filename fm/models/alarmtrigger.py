# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlarmTrigger
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from django.db import models
## NOC modules
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.main.models.timepattern import TimePattern
from noc.main.models.notificationgroup import NotificationGroup
from noc.main.models.pyrule import PyRule


class AlarmTrigger(models.Model):
    class Meta:
        db_table = "fm_alarmtrigger"
        app_label = "fm"
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
