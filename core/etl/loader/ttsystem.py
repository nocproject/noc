# ----------------------------------------------------------------------
# TTSystem loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseLoader
from ..models.ttsystem import TTSystemModel
from noc.fm.models.ttsystem import TTSystem


class TTMapLoader(BaseLoader):
    name = "ttsystem"
    model = TTSystem
    data_model = TTSystemModel
    fields = ["id", "name", "handler", "connection", "description"]
