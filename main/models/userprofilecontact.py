# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## UserProfileContact model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
## NOC modules
from userprofile import UserProfile
from timepattern import TimePattern
from notification import USER_NOTIFICATION_METHOD_CHOICES


class UserProfileContact(models.Model):
    class Meta:
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

    def __unicode__(self):
        return "%s %s %s" % (
            self.user_profile.user.username,
            self.time_pattern.name,
            self.notification_method
        )
