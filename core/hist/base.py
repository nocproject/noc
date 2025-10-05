# ----------------------------------------------------------------------
# Metrics Histograms
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import bisect

# Third-party modules
from atomicl import AtomicLong

DEFAULT_HIST_SCALE = 1000000


class Histogram(object):
    def __init__(self, config=None, scale=DEFAULT_HIST_SCALE):
        self.scale = DEFAULT_HIST_SCALE
        self.labels = [str(x) for x in config] + ["+Inf"]
        self.thresholds = [int(x * scale) for x in config]
        self.metrics = [AtomicLong(0) for _ in range(len(config) + 1)]
        self.total_sum = AtomicLong(0)
        self.total_count = AtomicLong(0)

    def register(self, value):
        i = bisect.bisect_left(self.thresholds, value)
        for x in self.metrics[i:]:
            x += 1
        self.total_sum += value
        self.total_count += 1

    def get_values(self):
        return [x.value for x in self.metrics]

    def iter_prom_metrics(self, name, labels):
        # Prepare labels
        ext_labels = ['%s="%s"' % (i.lower(), labels[i]) for i in labels]
        # Yield _bucket
        bucket_name = "%s_bucket" % name
        for label, metric in zip(self.labels, self.metrics):
            yield "# TYPE %s untyped" % bucket_name
            all_labels = [*ext_labels, 'le="%s"' % label]
            yield "%s{%s} %s" % (bucket_name, ",".join(all_labels), metric.value)
        # Yield _sum
        sum_name = "%s_sum" % name
        yield "# TYPE %s untyped" % sum_name
        yield "%s{%s} %s" % (
            sum_name,
            ",".join(ext_labels),
            float(self.total_sum.value) / self.scale,
        )
        # Yield _count
        count_name = "%s_count" % name
        yield "# TYPE %s untyped" % count_name
        yield "%s{%s} %s" % (count_name, ",".join(ext_labels), self.total_count.value)
