#!./bin/python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# SAE service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import contextlib
# Third-party modules
from psycopg2.pool import ThreadedConnectionPool
# NOC modules
from noc.core.service.base import Service
from noc.main.models.pool import Pool
from api.sae import SAEAPI
from noc.config import config


class SAEService(Service):
    name = "sae"
    process_name = "noc-%(name).10s-%(instance).2s"
    api = [SAEAPI]

    def __init__(self):
        super(SAEService, self).__init__()
        self.pool_cache = {}
        self.activators = {}
        self.pg_pool = None

    def load_pools(self):
        self.logger.info("Loading pools")
        for p in Pool.objects.all():
            self.pool_cache[str(p.id)] = p.name

    def on_activate(self):
        self.load_pools()
        self.pg_pool = ThreadedConnectionPool(
            1,
            config.sae.db_threads,
            **config.pg_connection_args
        )

    def get_pool_name(self, pool_id):
        """
        Returns pool name by id
        """
        return self.pool_cache.get(str(pool_id))

    @contextlib.contextmanager
    def get_pg_connect(self):
        connect = self.pg_pool.getconn()
        if not connect.autocommit:
            connect.autocommit = True
        try:
            yield connect
        finally:
            self.pg_pool.putconn(connect)

if __name__ == "__main__":
    SAEService().start()
