# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# cm.ValidationPolicy tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.cm.models.validationpolicy import ValidationPolicy


class TestCmValidationPolicy(BaseDocumentTest):
    model = ValidationPolicy
