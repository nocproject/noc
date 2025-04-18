# ---------------------------------------------------------------------
# UserContact model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.model.base import NOCModel
from noc.main.models.timepattern import TimePattern
from noc.main.models.notificationgroup import USER_NOTIFICATION_METHOD_CHOICES
from .user import User


class UserContact(NOCModel):
    class Meta(object):
        verbose_name = "User Profile Contact"
        verbose_name_plural = "User Profile Contacts"
        unique_together = [("user", "time_pattern", "notification_method", "params")]
        app_label = "aaa"
        db_table = "aaa_usercontact"

    user: User = models.ForeignKey(User, verbose_name="User", on_delete=models.CASCADE)
    time_pattern = models.ForeignKey(
        TimePattern, verbose_name="Time Pattern", on_delete=models.CASCADE
    )
    notification_method = models.CharField(
        "Method", max_length=16, choices=USER_NOTIFICATION_METHOD_CHOICES
    )
    params = models.CharField("Params", max_length=256)

    def __str__(self):
        return f"{self.user.username} {self.time_pattern.name if self.time_pattern else ''} {self.notification_method}"
