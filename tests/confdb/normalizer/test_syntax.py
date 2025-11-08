# ----------------------------------------------------------------------
# Test ConfDB syntax and generators
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.confdb.normalizer.base import BaseNormalizer


@pytest.mark.parametrize(
    ("name", "args", "paths"),
    [
        ("make_hostname", {"hostname": "test"}, ["system", "hostname", "test", {"replace": True}]),
        (
            "make_domain_name",
            {"domain_name": "example.com"},
            ["system", "domain-name", "example.com", {"replace": True}],
        ),
        ("make_prompt", {"prompt": "SW1>"}, ["system", "prompt", "SW1>", {"replace": True}]),
    ],
)
def test_syntax_gen(name, args, paths):
    normalizer = BaseNormalizer(None, None)
    gen = getattr(normalizer, name, None)
    assert gen, "Generator '%s' is not defined" % gen
    result = list(gen(**args))
    assert paths == result
