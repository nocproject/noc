# ----------------------------------------------------------------------
# Topo service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.services.topo.service import TopoService


if __name__ == "__main__":
    TopoService().start()
