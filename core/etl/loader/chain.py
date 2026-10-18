# ----------------------------------------------------------------------
# Loader chain
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# Third-party modules
import cachetools

# NOC modules
from noc.core.etl.loader.base import BaseLoader, etl_loader


class LoaderChain:
    def __init__(self, system) -> None:
        self.system = system
        self.loaders: dict[str, BaseLoader] = {}  # name -> loader
        self.lseq: list[BaseLoader] = []
        self.cache = cachetools.LRUCache(maxsize=1000)
        self.cache.__missing__ = self.get_cached

    def get_loader(self, name: str) -> BaseLoader:
        loader = self.loaders.get(name)
        if not loader:
            loader_cls = etl_loader.get(name)
            loader = loader_cls(self)
            self.loaders[name] = loader
            self.lseq.append(loader)
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
