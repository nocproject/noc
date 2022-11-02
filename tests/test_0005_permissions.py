# ----------------------------------------------------------------------
# Test application permissions
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.aaa.models.permission import Permission
from noc.core.service.loader import get_service
from noc.services.web.app.site import site


def test_permissions():
    site.service = get_service()
    Permission.sync()
    assert Permission.objects.count() > 0
