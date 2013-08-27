# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ObjectNotification
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
## NOC modules
from managedobjectselector import ManagedObjectSelector
from noc.main.models.notificationgroup import NotificationGroup
from noc.lib.template import render_message


class ObjectNotification(models.Model):
    class Meta:
        verbose_name = _("Managed Object Notification")
        verbose_name = _("Managed Object Notifications")
        db_table = "sa_objectnotification"
        app_label = "sa"

    selector = models.ForeignKey(
        ManagedObjectSelector,
        verbose_name=_("Selector"))
    notification_group = models.ForeignKey(
        NotificationGroup,
        verbose_name=_("Notification Group"))
    # Events
    config_changed = models.BooleanField(_("Config changed"))
    alarm_risen = models.BooleanField(_("Alarm risen"))
    alarm_cleared = models.BooleanField(_("Alarm cleared"))
    alarm_commented = models.BooleanField(_("Alarm commented"))
    new = models.BooleanField(_("New"))
    deleted = models.BooleanField(_("Deleted"))
    version_changed = models.BooleanField(_("Version changed"))
    interface_changed = models.BooleanField(_("Interface changed"))
    script_failed = models.BooleanField(_("Script failed"))
    config_policy_violation = models.BooleanField(_("Config policy violation"))

    def __unicode__(self):
        return u"%s, %s" % (self.selector, self.notification_group)

    @classmethod
    def render_message(cls, event_id, context):
        """
        Render template for event
        :param cls:
        :param event_id:
        :param context:
        :return: subject, body tuple
        """
        # Render template
        template = "object/%s.html" % event_id
        return render_message(template, context)
