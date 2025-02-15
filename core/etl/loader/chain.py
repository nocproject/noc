# ----------------------------------------------------------------------
# Loader chain
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Dict, List

# Third-party modules
import cachetools

# NOC modules
from .loader import loader as loader_loader
from noc.core.etl.loader.base import BaseLoader


class LoaderChain(object):
    def __init__(self, system):
        self.system = system
        self.loaders: Dict[str, BaseLoader] = {}  # name -> loader
        self.lseq: List[BaseLoader] = []
        self.cache = cachetools.LRUCache(maxsize=1000)
        self.cache.__missing__ = self.get_cached

    def get_loader(self, name: str) -> BaseLoader:
        loader = self.loaders.get(name)
        if not loader:
            lc = loader_loader.get_loader(name)
            loader = lc(self)
            self.loaders[name] = loader
            self.lseq += [loader]
        return loader

    def __iter__(self):
        yield from self.lseq

    def get_mappings(self, name):
        """
        Returns mappings for a loader *name*
        """
        return self.get_loader(name).mappings

    def get_cached(self, r):
        """
        Returns cached object reference
        """
        model, key = r
        try:
            return model.objects.get(id=key)
        except model.DoesNotExist:
            return None
