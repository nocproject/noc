# ----------------------------------------------------------------------
# noc.services.web.app.site test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC files
from noc.services.web.app.site import site


def test_autodiscover():
    site.autodiscover()
    assert site.apps
