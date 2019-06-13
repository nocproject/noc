# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Database models for main module
# ---------------------------------------------------------------------
# flake8: noqa
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from django.contrib.auth.models import Group
from .userprofile import UserProfile  # Cannot be moved, as referred from settings.py

