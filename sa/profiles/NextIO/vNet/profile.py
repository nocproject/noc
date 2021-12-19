# ---------------------------------------------------------------------
# Vendor: NextIO
# OS:     vNet
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "NextIO.vNet"

    pattern_syntax_error = rb"^ERROR: Invalid command -"
    pattern_operation_error = rb"^ERROR: "
    pattern_prompt = rb"^(?P<hostname>\S+)> "
