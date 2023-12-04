# ---------------------------------------------------------------------
# Action Loader
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.loader.base import BaseLoader
from .base import BaseAction


class ActionLoader(BaseLoader):
    name = "action"
    base_cls = BaseAction
    base_path = ("core", "runner", "actions")
    ignored_names = {"base", "loader"}


loader = ActionLoader()
