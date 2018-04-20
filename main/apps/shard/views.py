# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.shard application
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.main.models import Shard


class ShardApplication(ExtModelApplication):
    """
    Shard application
    """
    title = "Shard"
    menu = "Setup | Shards"
    model = Shard
