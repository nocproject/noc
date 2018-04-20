# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Unittests for Activator
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.test import ModelTestCase
from noc.sa.models import Activator
from noc.main.models import Shard


class ActivatorTestCase(ModelTestCase):
    model = Activator

    def get_data(self):
        shard = Shard.objects.all()[0]
        return [
            {
                "name": "A1",
                "is_active": True,
                "ip": "192.168.0.2",
                "to_ip": "192.168.0.2",
                "shard": shard
            },

            {
                "name": "A2",
                "is_active": True,
                "ip": "192.168.1.0",
                "to_ip": "192.168.1.255",
                "shard": shard
            },

            {
                "name": "A3",
                "is_active": True,
                "ip": "10.0.0.1",
                "to_ip": "10.0.0.1",
                "shard": shard
            },

            {
                "name": "A4",
                "is_active": True,
                "ip": "10.0.0.2",
                "to_ip": "10.0.0.2",
                "shard": shard
            }
        ]
