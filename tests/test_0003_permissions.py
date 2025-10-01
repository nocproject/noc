# ----------------------------------------------------------------------
# Test application permissions
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.aaa.models.permission import Permission
from noc.core.service.loader import get_service
from noc.services.web.base.site import site


@pytest.mark.fatal
def test_permissions(database):
    site.service = get_service()
    Permission.sync()
    assert Permission.objects.count() > 0
