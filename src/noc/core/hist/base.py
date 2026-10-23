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


class Histogram:
    def __init__(self, config=None, scale=DEFAULT_HIST_SCALE) -> None:
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
        ext_labels = [f'{i.lower()}="{labels[i]}"' for i in labels]
        # Yield _bucket
        bucket_name = f"{name}_bucket"
        for label, metric in zip(self.labels, self.metrics):
            yield f"# TYPE {bucket_name} untyped"
            all_labels = [*ext_labels, f'le="{label}"']
            yield f"{bucket_name}{{{','.join(all_labels)}}} {metric.value}"
        # Yield _sum
        sum_name = f"{name}_sum"
        yield f"# TYPE {sum_name} untyped"
        yield f"{sum_name}{{{','.join(ext_labels)}}} {float(self.total_sum.value) / self.scale}"
        # Yield _count
        count_name = f"{name}_count"
        yield f"# TYPE {count_name} untyped"
        yield f"{count_name}{{{','.join(ext_labels)}}} {self.total_count.value}"
