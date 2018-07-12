# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# sa.ManagedObjectProfile tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseModelTest
from noc.sa.models.managedobjectprofile import ManagedObjectProfile


class TestTestSaManagedObjectProfile(BaseModelTest):
    model = ManagedObjectProfile
