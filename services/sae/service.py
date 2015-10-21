#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SAE service
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.service.base import Service
from noc.main.models.pool import Pool
from api.sae import SAEAPI


class SAEService(Service):
    name = "sae"
    api = [SAEAPI]

    def __init__(self):
        super(SAEService, self).__init__()
        self.pool_cache = {}
        self.activators = {}

    def load_pools(self):
        self.logger.info("Loading pools")
        for p in Pool.objects.all():
            self.pool_cache[str(p.id)] = p.name

    def on_activate(self):
        self.load_pools()

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


if __name__ == "__main__":
    SAEService().start()
