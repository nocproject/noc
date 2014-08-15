## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Graphite-compatible storage interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import errno
import inspect
import fnmatch
import re
## NOC modules
from settings import config


class TimeSeriesDatabase(object):
    name = None

    rx_variant = re.compile(r"{([^}]*)}")

    def __init__(self):
        pass

    @classmethod
    def get_database(cls):
        sc = config.get("pm_storage", "type")
        scls = None
        m = __import__("noc.pm.storage.%s_storage" % sc, {}, {}, "*")
        for a in dir(m):
            o = getattr(m, a)
            if (inspect.isclass(o) and
                    issubclass(o, cls) and o.name == sc):
                scls = o
                break
        if not scls:
            raise ValueError("Invalid storage type '%s'" % sc)
        return scls()

    def initialize(self):
        """
        Initialize database
        """
        pass

    def write(self, metric, datapoints):
        """
        Persist datapoints into the database metric
        Datapoints are [(timestamp, value), ....]
        """
        raise NotImplementedError()

    def exists(self, metric):
        """
        Check metric is exists in database
        """
        raise NotImplementedError()

    def create(self, metric, **options):
        """
        Create database metric using default options
        """
        raise NotImplementedError()

    def get_metadata(self, metric, key):
        """
        Get metric metadata
        """
        raise NotImplementedError()

    def set_metadata(self, metric, key, value):
        """
        Modify metric metadata
        """
        raise NotImplementedError()

    @classmethod
    def ensure_path(cls, path):
        """
        Create all necessary directories
        """
        d = os.path.dirname(path)
        if not os.path.isdir(d):
            try:
                os.makedirs(d, 0755)
            except OSError, e:
                if e.errno != errno.EEXIST:
                    raise

    def fetch(self, metric, start, end):
        """
        Returns a all metric's value within range in form
        (start, end, step), [value1, ..., valueN]
        """
        raise NotImplementedError()

    def find(self, path_expr):
        """
        Find all metrics belonging to path expression
        """
        raise NotImplementedError()

    @classmethod
    def match_entries(cls, entries, pattern):
        def iter_patterns(p):
            """
            Expand {x,y} replacements
            """
            match = cls.rx_variant.search(p)
            if match:
                head = pattern[:match.start()]
                tail = pattern[match.end():]
                for v in match.group(1).split(","):
                    for vv in iter_patterns(head + v + tail):
                        yield vv
            else:
                yield p

        r = set()
        for p in iter_patterns(pattern):
            r.update(fnmatch.filter(entries, p))
        return sorted(r)

    def find_metrics(self, current_dir, path_expr):
        def _find_paths(d, patterns):
            """
            Yield all matching paths
            """
            pattern, rest = patterns[0], patterns[1:]
            entries = os.listdir(d)
            if rest:
                # Not last term in patter, follow directories
                subdirs = [e for e in entries
                           if os.path.isdir(os.path.join(d, e))]
                for sd in self.match_entries(subdirs, pattern):
                    for m in _find_paths(os.path.join(d, sd), rest):
                        yield "%s.%s" % (pattern, m)
            else:
                # Last term, find metrics
                for m in self.iter_metrics(d, pattern):
                    yield m

        p = path_expr.replace("\\", "").split(".")
        for path in _find_paths(current_dir, p):
            yield path

    def iter_metrics(self, d, pattern):
        """
        Yield all metrics in given directory, matching patterns
        """
        raise NotImplementedError()