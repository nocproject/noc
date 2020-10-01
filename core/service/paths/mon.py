# ----------------------------------------------------------------------
# /mon path
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from fastapi import APIRouter

# NOC modules
from noc.core.service.loader import get_service

router = APIRouter()

TR = str.maketrans('.-"', "___")


@router.get("/mon", tags=["internal"])
@router.get("/mon/", tags=["internal"])
async def mon():
    mdata = get_service().get_mon_data()
    response = {}
    for key in mdata:
        if isinstance(key, tuple):
            metric_name = key[0]
            for k in key[1:]:
                metric_name += "_%s" % "_".join(str(i) for i in k)
        else:
            metric_name = key.lower()
        cleared_name = str(metric_name).translate(TR)
        response[cleared_name] = mdata[key]
    return response
