# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Test script loader
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from nose2.tools import params
## NOC modules
from noc.core.profile.loader import loader


def test_iter_scripts():
    """ Check loader.iter_scripts() returns values """
    assert len(list(loader.iter_profiles())) > 0


@params(*tuple(loader.iter_profiles()))
def test_script_loading(name):
    """ Check profile can be loaded """
    profile = loader.get_profile(name)
    assert profile, "Cannot load script %s" % name
    profile.initialize()

