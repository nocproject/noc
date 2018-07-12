# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# gis.Division tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.gis.models.division import Division


class TestGisDivision(BaseDocumentTest):
    model = Division
