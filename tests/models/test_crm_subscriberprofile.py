# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# crm.SubscriberProfile tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.crm.models.subscriberprofile import SubscriberProfile


class TestCrmSubscriberProfile(BaseDocumentTest):
    model = SubscriberProfile
