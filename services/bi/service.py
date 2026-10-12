#!./bin/python
# ----------------------------------------------------------------------
# BI service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.base import BaseService


class BIService(BaseService):
    name = "bi"
    use_translation = True
    use_mongo = True
    traefik_routes_rule = "PathPrefix(`/api/bi`)"

    def __init__(self) -> None:
        super().__init__()
