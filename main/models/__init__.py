# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Database models for main module
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python Modules
import datetime

from django.contrib.auth.models import User, Group
from django.core.validators import MaxLengthValidator
from django.db import models
from django.db.models.signals import pre_save, pre_delete,\
                                     post_save, post_delete
from django.utils.translation import ugettext_lazy as _
from noc import settings
from noc.lib.periodic import periodic_registry

# Register periodics
periodic_registry.register_all()
from customfieldenumgroup import CustomFieldEnumGroup
from customfieldenumvalue import CustomFieldEnumValue
from customfield import CustomField
from resourcestate import ResourceState
from pyrule import PyRule, NoPyRuleException
from timepattern import TimePattern
from timepatternterm import TimePatternTerm
from notificationgroup import (
    NotificationGroup, NotificationGroupUser, NotificationGroupOther
)



from userprofile import UserProfile, UserProfileManager
from userprofilecontact import UserProfileContact
from dbtrigger import DBTrigger, model_choices
from systemnotification import SystemNotification

class Schedule(models.Model):
    class Meta:
        verbose_name = _("Schedule")
        verbose_name_plural = _("Schedules")
        ordering = ["periodic_name"]

    periodic_name = models.CharField(_("Periodic Task"), max_length=64)
    is_enabled = models.BooleanField(_("Enabled?"), default=False)
    time_pattern = models.ForeignKey(TimePattern,
                                     verbose_name=_("Time Pattern"))
    run_every = models.PositiveIntegerField(_("Run Every (secs)"),
                                     default=86400)
    timeout = models.PositiveIntegerField(_("Timeout (secs)"),
                                     null=True, blank=True)
    last_run = models.DateTimeField(_("Last Run"), blank=True, null=True)
    last_status = models.BooleanField(_("Last Status"), default=True)

    def __unicode__(self):
        return u"%s:%s" % (self.periodic_name, self.time_pattern.name)

    @property
    def periodic(self):
        return periodic_registry[self.periodic_name]

    def mark_run(self, start_time, status):
        """Set last run"""
        self.last_run = start_time
        self.last_status = status
        self.save()

    @classmethod
    def get_tasks(cls):
        """Get tasks required to run"""
        now = datetime.datetime.now()
        return [s for s in Schedule.objects.filter(is_enabled=True)
                if (s.time_pattern.match(now) and
                   (s.last_run is None or
                    s.last_run + datetime.timedelta(seconds=s.run_every) <= now))]

    @classmethod
    def reschedule(cls, name, days=0, minutes=0, seconds=0):
        """Reschedule tasks with name to launch immediately"""
        t = Schedule.objects.filter(periodic_name=name)[0]
        t.last_run = (datetime.datetime.now() -
                      datetime.timedelta(days=days, minutes=minutes,
                                         seconds=seconds))
        t.save()

from prefixtable import PrefixTable, PrefixTablePrefix
from template import Template
from systemtemtemplate import SystemTemplate
from checkpoint import Checkpoint
from favorites import Favorites
from tag import Tag
from sync import Sync

#
# Install triggers
#
if settings.IS_WEB and not settings.IS_TEST:
    DBTrigger.refresh_cache()  # Load existing triggers
    # Trigger cache syncronization
    post_save.connect(DBTrigger.refresh_cache, sender=DBTrigger)
    post_delete.connect(DBTrigger.refresh_cache, sender=DBTrigger)
    # Install signal hooks
    pre_save.connect(DBTrigger.pre_save_dispatch)
    post_save.connect(DBTrigger.post_save_dispatch)
    pre_delete.connect(DBTrigger.pre_delete_dispatch)
    post_delete.connect(DBTrigger.post_delete_dispatch)

#
# Monkeypatch to change User.username.max_length
#
User._meta.get_field("username").max_length = User._meta.get_field("email").max_length
User._meta.get_field("username").validators = [MaxLengthValidator(User._meta.get_field("username").max_length)]
User._meta.ordering = ["username"]
