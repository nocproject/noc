# ----------------------------------------------------------------------
# <describe module here>
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.models import iter_model_id


def test_iter_model_id():
    """
    Check iter_model_id is not empty
    """
    assert any(iter_model_id())
