# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# maintenance.MaintenanceType tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.maintenance.models.maintenancetype import MaintenanceType


class TestMaintenanceMaintenanceType(BaseDocumentTest):
    model = MaintenanceType
