# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# crm.SupplierProfile tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.crm.models.supplierprofile import SupplierProfile


class TestCrmSupplierProfile(BaseDocumentTest):
    model = SupplierProfile
