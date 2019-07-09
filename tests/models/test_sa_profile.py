# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# sa.Profile tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import bson

# NOC modules
from noc.sa.models.profile import Profile


def test_generic_profile_id():
    p = Profile.get_generic_profile_id()
    assert p
    assert isinstance(p, bson.ObjectId)
