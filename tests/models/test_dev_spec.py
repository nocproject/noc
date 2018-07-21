# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# dev.Spec tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.dev.models.spec import Spec


class TestDevSpec(BaseDocumentTest):
    model = Spec
