# ---------------------------------------------------------------------
# EventTrigger
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.db.models.base import Model
from django.db import models

# NOC modules
from noc.core.model.fields import DocumentReferenceField
from noc.main.models.timepattern import TimePattern
from noc.main.models.notificationgroup import NotificationGroup
from noc.main.models.template import Template
from noc.inv.models.resourcegroup import ResourceGroup


class EventTrigger(Model):
    class Meta(object):
        db_table = "fm_eventtrigger"
        app_label = "fm"
        verbose_name = "Event Trigger"
        verbose_name_plural = "Event Triggers"

    name = models.CharField("Name", max_length=64, unique=True)
    is_enabled = models.BooleanField("Is Enabled", default=True)
    description = models.CharField("Description", max_length=256, null=True, blank=True)
    event_class_re = models.CharField("Event class RE", max_length=256)
    condition = models.CharField("Condition", max_length=256, default="True")
    time_pattern = models.ForeignKey(
        TimePattern, verbose_name="Time Pattern", null=True, blank=True, on_delete=models.CASCADE
    )
    resource_group = DocumentReferenceField(ResourceGroup, null=True, blank=True)
    notification_group = models.ForeignKey(
        NotificationGroup,
        verbose_name="Notification Group",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    template = models.ForeignKey(
        Template, verbose_name="Template", null=True, blank=True, on_delete=models.CASCADE
    )
    handler = models.CharField("Handler", max_length=128, null=True, blank=True)

    def __str__(self):
        return "%s <<<%s>>>" % (self.event_class_re, self.condition)
