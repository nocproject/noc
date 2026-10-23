# ----------------------------------------------------------------------
# GrafanaDS API endpoint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from fastapi import APIRouter


router = APIRouter()


@router.get("/api/grafanads/")
def api_grafanads():
    return "OK"
