# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## UserProfile model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## Django modules
from django.db import models
from django.contrib.auth.models import User
## NOC modules
from noc import settings
from noc.lib.middleware import get_user


class UserProfileManager(models.Manager):
    """
    @todo: remove
    User Profile Manager
    Leave only current user's profile
    """
    def get_query_set(self):
        s = super(UserProfileManager, self)
        user = get_user()
        if user:
            # Create profile when necessary
            try:
                s.get_query_set().get(user=user)
            except UserProfile.DoesNotExist:
                UserProfile(user=user).save()
            return s.get_query_set().filter(user=user)
        else:
            return s.get_query_set()


class UserProfile(models.Model):
    """
    User profile
    """
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        app_label = "main"
        db_table = "main_userprofile"

    user = models.ForeignKey(User, unique=True)
    # User data
    preferred_language = models.CharField(
        "Preferred Language",
        max_length=16,
        null=True, blank=True,
        default=settings.LANGUAGE_CODE,
        choices=settings.LANGUAGES)
    theme = models.CharField(
        "Theme", max_length=32, null=True, blank=True)
    #
    objects = UserProfileManager()

    def __unicode__(self):
        return "%s's Profile" % self.user.username

    def save(self, **kwargs):
        user = get_user()
        if user and self.user != user:
            raise Exception("Invalid user")
        super(UserProfile, self).save(**kwargs)

    @property
    def contacts(self):
        return [(c.time_pattern, c.notification_method, c.params)
            for c in self.userprofilecontact_set.all()]

    @property
    def active_contacts(self):
        """
        Get list of currently active contacts

        :returns: List of (method, params)
        """
        now = datetime.datetime.now()
        return [(c.notification_method, c.params)
            for c in self.contacts if c.time_pattern.match(now)]
