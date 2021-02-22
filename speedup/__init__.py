# ----------------------------------------------------------------------
#  Copyright (C) 2007-2020 The NOC Project
#  See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os

if os.name == "nt":
    try:
        import pyximport
    except ImportError:
        raise NotImplementedError("Working on Windows without pyximport not supported")
    pyximport.install()
