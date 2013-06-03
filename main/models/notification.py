## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Notification model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python models
import datetime
## Django models
from django.db import models

NOTIFICATION_METHOD_CHOICES = [
    ("mail", "mail"),
    ("file", "file"),
    ("xmpp", "xmpp")
]

USER_NOTIFICATION_METHOD_CHOICES = [
    ("mail", "mail"),
    ("xmpp", "xmpp")
]


class Notification(models.Model):
    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        app_label = "main"
        db_table = "main_notification"

    timestamp = models.DateTimeField(
        "Timestamp", auto_now=True, auto_now_add=True)
    notification_method = models.CharField(
        "Method", max_length=16, choices=NOTIFICATION_METHOD_CHOICES)
    notification_params = models.CharField("Params", max_length=256)
    subject = models.CharField("Subject", max_length=256)
    body = models.TextField("Body")
    link = models.CharField(
        "Link", max_length=256, null=True, blank=True)
    next_try = models.DateTimeField(
        "Next Try", null=True, blank=True,
        default=datetime.datetime.now)
    actual_till = models.DateTimeField(
        "Actual Till", null=True, blank=True)

    def __unicode__(self):
        return self.subject
