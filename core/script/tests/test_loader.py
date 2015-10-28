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
from noc.core.script.loader import loader


def test_iter_scripts():
    """ Check loader.iter_scripts() returns values """
    assert len(list(loader.iter_scripts())) > 0


@params(*tuple(loader.iter_scripts()))
def test_script_loading(name):
    """ Check script can be loaded """
    assert loader.get_script(name), "Cannot load script %s" % name
