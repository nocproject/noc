# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# inv.ResourceGroup tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.inv.models.resourcegroup import ResourceGroup


class TestInvResourceGroup(BaseDocumentTest):
    model = ResourceGroup

    def test_clean_legacy_id(self):
        """
        Check _legacy_id field is clean
        :return:
        """
        left = ResourceGroup._get_collection().find_one({
            "_legacy_id": {
                "$exists": True
            }
        })
        assert left is None, "_legacy_id field has been left by migration"
