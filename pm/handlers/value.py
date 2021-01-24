# ----------------------------------------------------------------------
# Value handlers
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


def bw_percent(v, in_speed=None, out_speed=None, bandwidth=None, **kwargs):
    """
    Convert speed to speed to bandwidth percent ratio
    :param v:
    :param in_speed:
    :param out_speed:
    :param bandwidth:
    :param kwargs:
    :return:
    """
    value = v // 1000000
    if bandwidth:
        return value * 100 // (bandwidth // 1000)
    if in_speed:
        return value * 100 // (in_speed // 1000)
    if out_speed:
        return value * 100 // (out_speed // 1000)
    return v
