# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Peer module datasources
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.datasource import DataSource
from noc.peer.models import *


class PeerDS(DataSource):
    _name = "peer.Peer"
    
    def __init__(self, peer):
        self._data = Peer.get_peer(peer)
    
    @property
    def local_asn(self):
        return self._data.local_asn.asn if self._data else None

    @property
    def remote_asn(self):
        return self._data.remote_asn if self._data else None

    @property
    def description(self):
        return self._data.description if self._data else None

    @property
    def import_filter(self):
        return self._data.import_filter if self._data else None

    @property
    def export_filter(self):
        return self._data.export_filter if self._data else None

    