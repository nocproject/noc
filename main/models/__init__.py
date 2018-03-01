# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Database models for main module
# ---------------------------------------------------------------------
# flake8: noqa
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from __future__ import absolute_import
from django.contrib.auth.models import User, Group
from django.core.validators import MaxLengthValidator
from noc import settings
from noc.lib.periodic import periodic_registry
periodic_registry.register_all()
from .customfield import CustomField
from .resourcestate import ResourceState
from .pyrule import PyRule, NoPyRuleException
from .notificationgroup import NotificationGroup, NotificationGroupUser, NotificationGroupOther
from .userprofile import UserProfile, UserProfileManager
from .userprofilecontact import UserProfileContact
from .dbtrigger import DBTrigger, model_choices
from .systemnotification import SystemNotification
from .schedule import Schedule
from .prefixtable import PrefixTable, PrefixTablePrefix
from .template import Template
from .systemtemtemplate import SystemTemplate
from .checkpoint import Checkpoint
from .favorites import Favorites
from .tag import Tag
from .sync import Sync

#
# Install triggers
#
if settings.IS_WEB and not settings.IS_TEST:
    from django.db.models.signals import pre_save, pre_delete, post_save, post_delete
    DBTrigger.refresh_cache()  # Load existing triggers
    # Trigger cache syncronization
    post_save.connect(DBTrigger.refresh_cache, sender=DBTrigger)
    post_delete.connect(DBTrigger.refresh_cache, sender=DBTrigger)
    # Install signal hooks
    pre_save.connect(DBTrigger.pre_save_dispatch)
    post_save.connect(DBTrigger.post_save_dispatch)
    pre_delete.connect(DBTrigger.pre_delete_dispatch)
    post_delete.connect(DBTrigger.post_delete_dispatch)

#
# Monkeypatch to change User.username.max_length
#
User._meta.get_field("username").max_length = User._meta.get_field("email").max_length
User._meta.get_field("username").validators = [MaxLengthValidator(User._meta.get_field("username").max_length)]
User._meta.ordering = ["username"]
