# ----------------------------------------------------------------------
# DataStreamRequestHandler
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import tornado.web
import cachetools

# NOC modules
from noc.core.service.apiaccess import APIAccessRequestHandler, authenticated


@cachetools.cached
def get_format_role(ds, fmt):
    return ds.get_format_role(fmt)


class DataStreamRequestHandler(APIAccessRequestHandler):
    def initialize(self, service, datastream):
        self.service = service
        self.datastream = datastream

    def get_access_tokens_set(self):
        tokens = {"datastream:*", "datastream:%s" % self.datastream.name}
        fmt = self.get_arguments("format")
        if fmt:
            role = get_format_role(self.datastream, fmt[0])
            if role:
                tokens.add("datastream:%s" % role)
        return tokens

    @authenticated
    async def get(self, *args, **kwargs):
        # Get limits
        p_limit = self.get_arguments("limit")
        if p_limit:
            limit = int(p_limit[0])
        else:
            limit = 0
        if not limit:
            limit = self.datastream.DEFAULT_LIMIT
        limit = min(limit, self.datastream.DEFAULT_LIMIT)
        # Collect filters
        filters = self.get_arguments("filter") or []
        ids = self.get_arguments("id") or None
        if ids:
            filters += ["id(%s)" % ",".join(ids)]
        # Start from change
        change_id = self.get_arguments("from")
        if change_id:
            change_id = change_id[0]
        else:
            change_id = None
        # Format
        fmt = self.get_arguments("format")
        if fmt:
            fmt = fmt[0]
        else:
            fmt = None
        # block argument
        p_block = self.get_arguments("block")
        to_block = bool(p_block) and bool(int(p_block[0]))
        first_change = None
        last_change = None
        while True:
            r = []
            try:
                for item_id, change_id, data in self.datastream.iter_data(
                    limit=limit, filters=filters, change_id=change_id, fmt=fmt
                ):
                    if not first_change:
                        first_change = change_id
                    last_change = change_id
                    r += [data]
            except ValueError:
                raise tornado.web.HTTPError(400)
            if to_block and not r:
                await self.service.wait(self.datastream.name)
            else:
                break
        self.set_header("Cache-Control", "no-cache")
        self.set_header("Content-Type", "application/json")
        self.set_header("X-NOC-DataStream-Total", str(self.datastream.get_total()))
        self.set_header("X-NOC-DataStream-Limit", str(limit))
        if first_change:
            self.set_header("X-NOC-DataStream-First-Change", str(first_change))
        if last_change:
            self.set_header("X-NOC-DataStream-Last-Change", str(last_change))
        self.write("[%s]" % ",".join(r))
