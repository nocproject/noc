# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## peer.maintainer application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.peer.models import Maintainer, Person
from noc.sa.interfaces.base import (ListOfParameter, ModelParameter,
                                    StringParameter)


class MaintainerApplication(ExtModelApplication):
    """
    Maintainers application
    """
    title = "Maintainers"
    menu = "Setup | Maintainers"
    model = Maintainer

