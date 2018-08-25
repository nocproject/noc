# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# AlarmTrigger
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.db import models
# NOC modules
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.main.models.timepattern import TimePattern
from noc.main.models.notificationgroup import NotificationGroup
from noc.main.models.template import Template


class AlarmTrigger(models.Model):
    class Meta(object):
        db_table = "fm_alarmtrigger"
        app_label = "fm"
        verbose_name = "Alarm Trigger"
        verbose_name_plural = "Alarm Triggers"

    name = models.CharField("Name", max_length=64, unique=True)
    is_enabled = models.BooleanField("Is Enabled", default=True)
    description = models.CharField(
        "Description",
        max_length=256, null=True, blank=True)
    alarm_class_re = models.CharField("Alarm class RE", max_length=256)
    condition = models.CharField("Condition", max_length=256, default="True")
    time_pattern = models.ForeignKey(TimePattern,
                                     verbose_name="Time Pattern",
                                     null=True, blank=True)
    selector = models.ForeignKey(ManagedObjectSelector,
                                 verbose_name="Managed Object Selector",
                                 null=True, blank=True)
    notification_group = models.ForeignKey(NotificationGroup,
                                           verbose_name="Notification Group",
                                           null=True, blank=True)
    template = models.ForeignKey(Template,
                                 verbose_name="Template",
                                 null=True, blank=True)
    handler = models.CharField("Handler",
                               max_length=128, null=True, blank=True)

    def __unicode__(self):
        return "%s <<<%s>>>" % (self.alarm_class_re, self.condition)
