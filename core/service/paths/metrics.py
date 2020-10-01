# ----------------------------------------------------------------------
# /metrics path
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

# NOC modules
from noc.config import config
from noc.core.service.loader import get_service

router = APIRouter()
TR = str.maketrans('.-"', "___")


@router.get("/metrics", tags=["internal"])
@router.get("/metrics/", tags=["internal"])
async def metrics():
    service = get_service()
    labels = {"service": service.name, "node": config.node}
    if service.pooled:
        labels["pool"] = config.pool
    if hasattr(service, "slot_number"):
        labels["slot"] = service.slot_number
    out = []
    mdata = service.get_mon_data()
    for key in mdata:
        if key == "pid":
            continue
        metric_name = key
        local_labels = {}
        if isinstance(mdata[key], (bool, str)):
            continue
        if isinstance(key, tuple):
            metric_name = key[0]
            for k in key[1:]:
                local_labels.update({k[0]: k[1]})
        local_labels.update(labels)
        cleared_name = str(metric_name).translate(TR).lower()
        value = mdata[key]
        if value is None:
            continue
        if hasattr(value, "iter_prom_metrics"):
            out += list(value.iter_prom_metrics(cleared_name, local_labels))
        else:
            out_labels = ",".join(['%s="%s"' % (i.lower(), local_labels[i]) for i in local_labels])
            out += ["# TYPE %s untyped" % cleared_name]
            out += ["%s{%s} %s" % (cleared_name, out_labels, value)]
    return PlainTextResponse(
        content="\n".join(out) + "\n", headers={"Content-Type": "text/plain; version=0.0.4"}
    )
