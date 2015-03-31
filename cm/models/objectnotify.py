# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Object notifications
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
## NOC modules
from noc.main.models.notificationgroup import NotificationGroup
from noc.sa.models.administrativedomain import AdministrativeDomain

OBJECT_TYPES = ["config", "dns", "prefix-list", "rpsl"]
OBJECT_TYPE_CHOICES = [(x, x) for x in OBJECT_TYPES if x != "config"]


class ObjectNotify(models.Model):
    class Meta:
        app_label = "cm"
        db_table = "cm_objectnotify"
        verbose_name = "Object Notify"
        verbose_name_plural = "Object Notifies"

    type = models.CharField("Type", max_length=16, choices=OBJECT_TYPE_CHOICES)
    administrative_domain = models.ForeignKey(AdministrativeDomain,
                                              verbose_name="Administrative Domain",
                                              blank=True, null=True)
    notify_immediately = models.BooleanField("Notify Immediately")
    notify_delayed = models.BooleanField("Notify Delayed")
    notification_group = models.ForeignKey(NotificationGroup,
                                           verbose_name="Notification Group")

    def __unicode__(self):
        return u"(%s, %s, %s)" % (self.type, self.administrative_domain,
                                  self.notification_group)

    def get_absolute_url(self):
        return site.reverse("cm:objectnotify:change", self.id)
