# ----------------------------------------------------------------------
# Model loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.loader.base import BaseLoader
from .base import BaseModel


class ModelLoader(BaseLoader):
    name = "etlmodel"
    base_cls = BaseModel
    base_path = ("core", "etl", "models")
    ignored_names = {"base", "loader"}


# Create singleton object
loader = ModelLoader()
