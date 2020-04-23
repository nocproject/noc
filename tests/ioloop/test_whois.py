# ----------------------------------------------------------------------
# whois client test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.ioloop.whois import whois


@pytest.mark.parametrize("domain", ["getnoc.com", "nocproject.org"])
def test_whois_domain(domain):
    data = dict(whois(domain))
    assert "domain" in data
    assert data["domain"].lower() == domain.lower()
    assert "paid-till" in data
