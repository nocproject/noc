# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Object notifications
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import six
from django.db import models

# NOC modules
from noc.core.model.base import NOCModel
from noc.main.models.notificationgroup import NotificationGroup
from noc.sa.models.administrativedomain import AdministrativeDomain

OBJECT_TYPES = ["config", "dns", "prefix-list", "rpsl"]
OBJECT_TYPE_CHOICES = [(x, x) for x in OBJECT_TYPES if x != "config"]


@six.python_2_unicode_compatible
class ObjectNotify(NOCModel):
    class Meta(object):
        app_label = "cm"
        db_table = "cm_objectnotify"
        verbose_name = "Object Notify"
        verbose_name_plural = "Object Notifies"

    type = models.CharField("Type", max_length=16, choices=OBJECT_TYPE_CHOICES)
    administrative_domain = models.ForeignKey(
        AdministrativeDomain,
        verbose_name="Administrative Domain",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    notify_immediately = models.BooleanField("Notify Immediately", default=False)
    notify_delayed = models.BooleanField("Notify Delayed", default=False)
    notification_group = models.ForeignKey(
        NotificationGroup, verbose_name="Notification Group", on_delete=models.CASCADE
    )

    def __str__(self):
        return "(%s, %s, %s)" % (self.type, self.administrative_domain, self.notification_group)
