# ----------------------------------------------------------------------
# Internal monitoring metrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.config import config
from .base import Histogram


hists = {}


def get_hist(*args):
    hist = hists.get(args, False)
    if hist is False:
        cfg = config.get_hist_config(args[0])
        if cfg:
            hist = Histogram(cfg)
        else:
            hist = None
        hists[args] = hist
    return hist


def apply_hists(d):
    """
    Apply histogram values to dict d
    :param d: Dictionary
    :return:
    """
    d.update(hists)
