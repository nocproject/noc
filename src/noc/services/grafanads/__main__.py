# ----------------------------------------------------------------------
# GrafanaDS service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.services.grafanads.service import GrafanaDSService


if __name__ == "__main__":
    GrafanaDSService().start()
