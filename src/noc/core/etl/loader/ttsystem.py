# ----------------------------------------------------------------------
# TTSystem loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.fm.models.ttsystem import TTSystem as TTSystemModel

from ..models.ttsystem import TTSystem
from .base import BaseLoader


class TTMapLoader(BaseLoader):
    name = "ttsystem"
    model = TTSystemModel
    data_model = TTSystem
