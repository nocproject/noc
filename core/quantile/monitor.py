# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Internal monitoring metrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from noc.config import config
from .base import Summary, TargetedStream

DEFAULT_TARGETS = [(q, config.metrics.default_quantiles_epsilon)
                   for q in config.metrics.default_quantiles]
DEFAULT_QUANTILE_SCALE = 1000000


class Quantile(Summary):
    def __init__(self, scale=DEFAULT_QUANTILE_SCALE):
        super(Quantile, self).__init__(
            config.metrics.default_quantiles_window, 1,
            TargetedStream, config.metrics.default_quantiles_buffer, DEFAULT_TARGETS)
        self.scale = scale

    def iter_prom_metrics(self, name, labels):
        # Prepare labels
        ext_labels = ['%s="%s"' % (i.lower(), labels[i]) for i in labels]
        for quantile in config.metrics.default_quantiles:
            value, = self.query(quantile, 0)
            all_labels = ext_labels + [
                "quantile=\"%s\"" % quantile,
                "window=\"%s\"" % config.metrics.default_quantiles_window
            ]
            yield "# TYPE %s untyped" % name
            yield "%s{%s} %s" % (name, ",".join(all_labels), float(value) / self.scale)


quantiles = {}


def get_quantile(*args):
    quantile = quantiles.get(args, False)
    if quantile is False:
        if config.get_quantiles_config(args[0]):
            quantile = Quantile()
        else:
            quantile = None
        quantiles[args] = quantile
    return quantile


def apply_quantiles(d):
    """
    Apply histogram values to dict d
    :param d: Dictionary
    :return:
    """
    d.update(quantiles)
