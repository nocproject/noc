# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# UserProfileContact model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-party modules modules
import six
from django.db import models
# NOC modules
from .userprofile import UserProfile
from .timepattern import TimePattern
from .notificationgroup import USER_NOTIFICATION_METHOD_CHOICES


@six.python_2_unicode_compatible
class UserProfileContact(models.Model):
    class Meta(object):
        verbose_name = "User Profile Contact"
        verbose_name_plural = "User Profile Contacts"
        unique_together = [("user_profile", "time_pattern",
                            "notification_method", "params")]
        app_label = "main"
        db_table = "main_userprofilecontact"

    user_profile = models.ForeignKey(
        UserProfile, verbose_name="User Profile")
    time_pattern = models.ForeignKey(
        TimePattern, verbose_name="Time Pattern")
    notification_method = models.CharField(
        "Method", max_length=16,
        choices=USER_NOTIFICATION_METHOD_CHOICES)
    params = models.CharField("Params", max_length=256)

    def __str__(self):
        return "%s %s %s" % (
            self.user_profile.user.username,
            self.time_pattern.name,
            self.notification_method
        )
