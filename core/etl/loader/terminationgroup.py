# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Termination Group loader
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from noc.sa.models.terminationgroup import TerminationGroup

## NOC modules
from base import BaseLoader


class TerminationGroupLoader(BaseLoader):
    """
    Administrative division loader
    """
    name = "terminationgroup"
    model = TerminationGroup
    fields = [
        "id",
        "name",
        "description"
    ]
