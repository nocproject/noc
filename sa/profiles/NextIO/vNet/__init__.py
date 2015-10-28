# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: NextIO
## OS:     vNet
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "NextIO.vNet"
    pattern_syntax_error = r"^ERROR: Invalid command -"
    pattern_operation_error = r"^ERROR: "
    pattern_prompt = r"^(?P<hostname>\S+)> "
