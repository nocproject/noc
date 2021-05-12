# ----------------------------------------------------------------------
# DCS utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.ioloop.util import run_sync
from .loader import get_dcs


async def resolve_async(
    name, hint=None, wait=True, timeout=None, full_result=False, near=False, critical=False
):
    dcs = get_dcs()
    try:
        if near:
            r = await dcs.resolve_near(
                name,
                hint=hint,
                wait=wait,
                timeout=timeout,
                full_result=full_result,
                critical=critical,
            )
        else:
            r = await dcs.resolve(
                name,
                hint=hint,
                wait=wait,
                timeout=timeout,
                full_result=full_result,
                critical=critical,
                track=False,
            )
    finally:
        dcs.stop()
    return r


def resolve(
    name, hint=None, wait=True, timeout=None, full_result=False, near=False, critical=False
):
    """
    Returns *hint* when service is active or new service
    instance,
    :param name:
    :param hint:
    :param wait:
    :param timeout:
    :param full_result:
    :param near:
    :return:
    """

    async def _resolve():
        return await resolve_async(
            name=name,
            hint=hint,
            wait=wait,
            timeout=timeout,
            full_result=full_result,
            near=near,
            critical=critical,
        )

    return run_sync(_resolve)
