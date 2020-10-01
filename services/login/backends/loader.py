# ----------------------------------------------------------------------
# Auth Backend loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.loader.base import BaseLoader
from .base import BaseAuthBackend


class AuthBackendLoader(BaseLoader):
    name = "authbackend"
    base_cls = BaseAuthBackend
    base_path = ("services", "login", "backends")
    ignored_names = {"base"}


loader = AuthBackendLoader()
