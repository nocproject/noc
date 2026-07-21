# ----------------------------------------------------------------------
# Report Source Base Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# Python Modules
from noc.core.reporter.band import Band
from noc.core.reporter.types import BandFormat


class ReportSource:
    """
    Class for old-compatible report format when Data and Format union in one source
    """

    name = None

    def get_formats(self) -> dict[str, BandFormat]:
        """
        Report Format describe
        :return:
        """

    def get_parameters(self):
        """
        Return Available report Parameters
        :return:
        """

    def get_data(self, request, **kwargs) -> list[Band]:
        """
        Return Report Data
        :return:
        """
