# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# SystemNotification
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# Third-party modules
import six
from django.db import models

# NOC modules
from noc.core.model.base import NOCModel
from .notificationgroup import NotificationGroup


@six.python_2_unicode_compatible
class SystemNotification(NOCModel):
    """
    System Notifications
    """

    class Meta(object):
        app_label = "main"
        db_table = "main_systemnotification"
        verbose_name = "System Notification"
        verbose_name_plural = "System Notifications"

    name = models.CharField("Name", max_length=64, unique=True)
    notification_group = models.ForeignKey(
        NotificationGroup,
        verbose_name="Notification Group",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return self.name

    @classmethod
    def get_notification_group(cls, name):
        try:
            sn = SystemNotification.objects.get(name=name)
            return sn.notification_group
        except SystemNotification.DoesNotExist:  # Ignore undefined notifications
            return None

    @classmethod
    def notify(cls, name, subject, body, link=None):
        n = cls.get_notification_group(name)
        if n:
            n.notify(subject=subject, body=body, link=link)
