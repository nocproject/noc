# ----------------------------------------------------------------------
# Data types
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any

# Third-party modules
from pydantic import StrictInt, StrictFloat

ValueType = int | float
StrictValueType = StrictInt | StrictFloat
FactoryCtx = dict[str, Any]
