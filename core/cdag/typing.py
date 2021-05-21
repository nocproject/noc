# ----------------------------------------------------------------------
# Data types
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, Dict, Union

# Third-party modules
from pydantic import StrictInt, StrictFloat

ValueType = Union[int, float]
StrictValueType = Union[StrictInt, StrictFloat]
FactoryCtx = Dict[str, Any]
