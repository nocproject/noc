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
from .userprofile import UserProfile  # Cannot be moved, as referred from settings.py
#
# Monkeypatch to change User.username.max_length
#
User._meta.get_field("username").max_length = User._meta.get_field("email").max_length
User._meta.get_field("username").validators = [MaxLengthValidator(User._meta.get_field("username").max_length)]
User._meta.ordering = ["username"]
