# ----------------------------------------------------------------------
# Internal monitoring metrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.config import config
from .base import Summary, TargetedStream

DEFAULT_TARGETS = [
    (q, config.perfomance.default_quantiles_epsilon) for q in config.perfomance.default_quantiles
]
DEFAULT_QUANTILE_SCALE = 1000000
Q_SUFFIX = "_@q"
Q_SUFFIX_LEN = len(Q_SUFFIX)


class Quantile(Summary):
    def __init__(self, scale=DEFAULT_QUANTILE_SCALE):
        super().__init__(
            config.perfomance.default_quantiles_window,
            1,
            TargetedStream,
            config.perfomance.default_quantiles_buffer,
            DEFAULT_TARGETS,
        )
        self.scale = scale

    def iter_prom_metrics(self, name, labels):
        # Avoid clash with histograms
        if name.endswith(Q_SUFFIX):
            name = name[:-Q_SUFFIX_LEN]
        # Prepare labels
        ext_labels = ['%s="%s"' % (i.lower(), labels[i]) for i in labels]
        for quantile in config.perfomance.default_quantiles:
            (value,) = self.query(quantile, 0)
            all_labels = [
                *ext_labels,
                'quantile="%s"' % quantile,
                'window="%s"' % config.perfomance.default_quantiles_window,
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
    for x in quantiles:
        if isinstance(x, tuple):
            xk = (x[0] + Q_SUFFIX, *x[1:])
        else:
            xk = x + Q_SUFFIX
        d[xk] = quantiles[x]
