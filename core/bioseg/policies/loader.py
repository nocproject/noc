# ----------------------------------------------------------------------
# BioSegPolicy loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.loader.base import BaseLoader
from .base import BaseBioSegPolicy


class BioSegPolicyLoader(BaseLoader):
    name = "bioseg"
    base_cls = BaseBioSegPolicy
    base_path = ("core", "bioseg", "policies")


# Create singleton object
loader = BioSegPolicyLoader()
