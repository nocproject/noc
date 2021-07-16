# ----------------------------------------------------------------------
# Administrative label loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseLoader
from ..models.label import Label
from noc.main.models.label import Label as LabelModel


class LabelLoader(BaseLoader):
    """
    Label loader
    """

    name = "label"
    model = LabelModel
    data_model = Label
