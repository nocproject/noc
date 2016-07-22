#!/usr/bin/env python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SAE service
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import contextlib
## NOC modules
from noc.core.service.base import Service
from noc.main.models.pool import Pool
from api.sae import SAEAPI
from noc.core.config.base import config
from pgpool import PreparedConnectionPool


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
        self.pg_pool = PreparedConnectionPool(
            1,
            self.config.db_threads,
            **config.pg_connection_args
        )

    def get_pool_name(self, pool_id):
        """
        Returns pool name by id
        """
        return self.pool_cache.get(str(pool_id))

    def get_activator(self, pool):
        """
        Returns RPC service for pool
        """
        activator = self.activators.get(pool)
        if not activator:
            activator = self.open_rpc("activator", pool=pool)
            self.activators[pool] = activator
        return activator

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
