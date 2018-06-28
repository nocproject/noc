# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Test application permissions
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.main.models.permission import Permission
from noc.core.service.loader import get_service
from noc.lib.app.site import site


def test_permissions():
    site.service = get_service()
    Permission.sync()
    assert Permission.objects.count() > 0
