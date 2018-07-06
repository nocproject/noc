# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# phone.PhoneNumberProfile tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.phone.models.phonenumberprofile import PhoneNumberProfile


class TestPhonePhoneNumberProfile(BaseDocumentTest):
    model = PhoneNumberProfile
