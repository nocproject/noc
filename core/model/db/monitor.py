# ----------------------------------------------------------------------
# PostgreSQL connection monitoring
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import psycopg2.extensions

# NOC modules
from noc.core.span import Span
from noc.core.hist.monitor import get_hist
from noc.core.quantile.monitor import get_quantile


class SpanCursor(psycopg2.extensions.cursor):
    def execute(self, query, vars=None):
        label = query.split(None, 1)[0].lower()[:10]
        with Span(
            service="postgres",
            hist=get_hist("postgres", ("command", label)),
            quantile=get_quantile("postgres", ("command", label)),
            in_label=label,
        ):
            super(SpanCursor, self).execute(query, vars)
