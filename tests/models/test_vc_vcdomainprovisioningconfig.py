# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# vc.VCDomainProvisioningConfig tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseModelTest
from noc.vc.models.vcdomainprovisioningconfig import VCDomainProvisioningConfig


class TestTestVcVCDomainProvisioningConfig(BaseModelTest):
    model = VCDomainProvisioningConfig
