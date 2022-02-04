# ----------------------------------------------------------------------
# Calculator Loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.loader.base import BaseLoader
from .base import BaseCalculator


class CalculatorLoader(BaseLoader):
    name = "calculator"
    ignored_names = {"base", "loader"}
    base_cls = BaseCalculator
    base_path = ("services", "web", "apps", "main", "calculator", "calculators")


# Create singleton object
loader = CalculatorLoader()
