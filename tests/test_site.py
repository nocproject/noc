# ----------------------------------------------------------------------
# noc.services.web.base.site test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC files
from noc.services.web.base.site import site


def test_autodiscover():
    site.autodiscover()
    assert site.apps
