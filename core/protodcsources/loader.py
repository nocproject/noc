# ----------------------------------------------------------------------
# Protocol Discriminator Source Loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.loader.base import BaseLoader
from .base import BaseDiscriminatorSource


class BaseProtocolDiscriminatorLoader(BaseLoader):
    name = "discriminatorsource"
    base_cls = BaseDiscriminatorSource
    base_path = ("core", "protodcsources")
    ignored_names = {"base", "loader"}


# Create singleton object
loader = BaseProtocolDiscriminatorLoader()
