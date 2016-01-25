# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Loader chain
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
import cachetools
## NOC modules
from loader import loader as loader_loader


class LoaderChain(object):
    def __init__(self, system):
        self.system = system
        self.loaders = {}  # name -> loader
        self.lseq = []
        self.cache = cachetools.LRUCache(
            maxsize=1000,
            missing=self.get_cached
        )

    def get_loader(self, name):
        loader = self.loaders.get(name)
        if not loader:
            lc = loader_loader.get_loader(name)
            loader = lc(self)
            self.loaders[name] = loader
            self.lseq += [loader]
        return loader

    def __iter__(self):
        for loader in self.lseq:
            yield loader

    def get_mappings(self, name):
        """
        Retuns mappings for a loader *name*
        """
        return self.get_loader(name).mappings

    def get_cached(self, r):
        """
        Returns cached object reference
        """
        model, key = r
        return model.objects.get(id=key)
