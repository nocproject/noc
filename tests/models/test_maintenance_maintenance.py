# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# maintenance.Maintenance tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.maintenance.models.maintenance import Maintenance


class TestMaintenanceMaintenance(BaseDocumentTest):
    model = Maintenance
