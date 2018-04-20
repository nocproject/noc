# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# UserProfile model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
# Django modules
from django.db import models
from django.contrib.auth.models import User
# NOC modules
from noc import settings
from noc.core.middleware.tls import get_user
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce


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
<<<<<<< HEAD
    class Meta(object):
=======
    class Meta:
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD
    # Heatmap position
    heatmap_lon = models.FloatField("Longitude", blank=True, null=True)
    heatmap_lat = models.FloatField("Latitude", blank=True, null=True)
    heatmap_zoom = models.IntegerField("Zoom", blank=True, null=True)

=======
    theme = models.CharField(
        "Theme", max_length=32, null=True, blank=True)
    preview_theme = models.CharField(
        "Preview Theme", max_length=32, null=True, blank=True)
    #
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD
        return [
            (c.time_pattern, c.notification_method, c.params)
=======
        return [(c.time_pattern, c.notification_method, c.params)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            for c in self.userprofilecontact_set.all()]

    @property
    def active_contacts(self):
        """
        Get list of currently active contacts

        :returns: List of (method, params)
        """
        now = datetime.datetime.now()
<<<<<<< HEAD
        return [
            (c.notification_method, c.params)
            for c in self.contacts if c.time_pattern.match(now)]

# Avoid circular references
# No delete, fixed 'UserProfile' object has no attribute 'userprofilecontact_set'
from .userprofilecontact import UserProfileContact  # noqa
=======
        return [(c.notification_method, c.params)
            for c in self.contacts if c.time_pattern.match(now)]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
