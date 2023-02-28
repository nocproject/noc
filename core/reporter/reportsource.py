# ----------------------------------------------------------------------
# Report Source Base Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List

# Python Modules
from .report import BandData
from .types import BandFormat


class ReportSource(object):
    """
    Class for old-compatible report format when Data and Format union in one source
    """

    name = None

    def get_format(self) -> BandFormat:
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

    def get_data(self, request, **kwargs) -> List[BandData]:
        """
        Return Report Data
        :param request:
        :param kwargs:
        :return:
        """
        ...
