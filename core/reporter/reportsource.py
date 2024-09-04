# ----------------------------------------------------------------------
# Report Source Base Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List, Dict

# Python Modules
from .report import Band
from .types import BandFormat


class ReportSource(object):
    """
    Class for old-compatible report format when Data and Format union in one source
    """

    name = None

    def get_formats(self) -> Dict[str, BandFormat]:
        """
        Report Format describe
        :return:
        """
        ...

    def get_parameters(self):
        """
        Return Available report Parameters
        :return:
        """
        ...

    def get_data(self, request, **kwargs) -> List[Band]:
        """
        Return Report Data
        :param request:
        :param kwargs:
        :return:
        """
        ...
