# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# cm.ValidationRule tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.cm.models.validationrule import ValidationRule


class TestCmValidationRule(BaseDocumentTest):
    model = ValidationRule
