# ----------------------------------------------------------------------
# noc.core.forms unittests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest
from django import forms
from django.core.wsgi import get_wsgi_application

# NOC modules
from noc.core.forms import NOCForm

app = get_wsgi_application()


class Form(NOCForm):
    charf = forms.CharField(required=True)
    intf = forms.IntegerField(min_value=18)


@pytest.mark.parametrize(
    ("charf", "intf", "expected"),
    [
        ("field1", 18, True),
        ("field2", 17, False),
        ("field3", None, False),
        ("", 18, False),
        (None, 18, False),
    ],
)
def test_f(charf, intf, expected):
    f = Form(data={"charf": charf, "intf": intf})
    assert f.is_valid() is expected
