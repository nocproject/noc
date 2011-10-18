# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.oidalias application
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.fm.models import OIDAlias


class OIDAliasApplication(ExtDocApplication):
    """
    OIDAlias application
    """
    title = "OID Aliases"
    menu = "Setup | OID Aliases"
    model = OIDAlias
