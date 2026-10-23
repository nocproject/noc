# ----------------------------------------------------------------------
# Mongo connection monitoring
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import local

# Third-party modules
import pymongo.monitoring

# NOC modules
from noc.core.hist.monitor import get_hist
from noc.core.quantile.monitor import get_quantile
from noc.core.span import Span

tls = local()


class MongoCommandSpan(pymongo.monitoring.CommandListener):
    def started(self, event):
        span = Span(
            service="mongo",
            hist=get_hist("mongo", ("command", event.command_name)),
            quantile=get_quantile("mongo", ("command", event.command_name)),
            in_label=event.command_name,
        )
        setattr(tls, str(event.request_id), span)
        span.__enter__()

    def succeeded(self, event):
        span = getattr(tls, str(event.request_id), None)
        if None:
            return  # Missed span
        span.__exit__(None, None, None)
        delattr(tls, str(event.request_id))

    def failed(self, event):
        self.succeeded(event)
