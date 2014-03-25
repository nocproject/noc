## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## asset_discovery helpers
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------


def get_name(object, managed_object=None):
    """
    Generate discovered object's name
    """
    name = None
    if managed_object:
        name = managed_object.name
        sm = object.get_data("stack", "member")
        if sm is not None:
            # Stack member
            name += "#%s" % sm
    return name
