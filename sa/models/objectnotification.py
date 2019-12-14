# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ObjectNotification
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# Third-party modules
import six
from noc.core.translation import ugettext as _
from django.db import models

# NOC modules
from noc.core.model.base import NOCModel
from noc.main.models.notificationgroup import NotificationGroup
from noc.lib.template import render_message
from .managedobjectselector import ManagedObjectSelector


@six.python_2_unicode_compatible
class ObjectNotification(NOCModel):
    class Meta(object):
        verbose_name = _("Managed Object Notification")
        db_table = "sa_objectnotification"
        app_label = "sa"

    selector = models.ForeignKey(
        ManagedObjectSelector, verbose_name=_("Selector"), on_delete=models.CASCADE
    )
    notification_group = models.ForeignKey(
        NotificationGroup, verbose_name=_("Notification Group"), on_delete=models.CASCADE
    )
    # Events
    config_changed = models.BooleanField(_("Config changed"), default=False)
    alarm_risen = models.BooleanField(_("Alarm risen"), default=False)
    alarm_reopened = models.BooleanField(_("Alarm reopened"), default=False)
    alarm_cleared = models.BooleanField(_("Alarm cleared"), default=False)
    alarm_commented = models.BooleanField(_("Alarm commented"), default=False)
    new = models.BooleanField(_("New"), default=False)
    deleted = models.BooleanField(_("Deleted"), default=False)
    version_changed = models.BooleanField(_("Version changed"), default=False)
    interface_changed = models.BooleanField(_("Interface changed"), default=False)
    script_failed = models.BooleanField(_("Script failed"), default=False)
    config_policy_violation = models.BooleanField(_("Config policy violation"), default=False)

    def __str__(self):
        return "%s, %s" % (self.selector, self.notification_group)

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
