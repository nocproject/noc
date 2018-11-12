# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Model loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import os
import threading
# NOC modules
from noc.config import config
from noc.core.loader.base import BaseLoader
from .model import Model


class ModelLoader(BaseLoader):
    name = "bi"
    IGNORED_MODELS = {"dashboard", "dashboardlayout"}

    def __init__(self):
        super(ModelLoader, self).__init__()
        self.models = {}  # Load models
        self.lock = threading.Lock()
        self.all_models = set()

    def get_model(self, name):
        with self.lock:
            model = self.models.get(name)
            if not model:
                self.logger.info("Loading loader %s", name)
                if not self.is_valid_name(name):
                    self.logger.error("Invalid loader name: %s", name)
                    return None
                for p in config.get_customized_paths("", prefer_custom=True):
                    path = os.path.join(p, "bi", "models", "%s.py" % name)
                    if not os.path.exists(path):
                        continue
                    if p:
                        # Customized model
                        base_name = os.path.basename(os.path.dirname(p))
                        module_name = "%s.bi.models.%s" % (base_name, name)
                    else:
                        # Common model
                        module_name = "noc.bi.models.%s" % name
                    model = self.find_class(module_name, Model, name)
                    if model:
                        if not hasattr(model, "_meta"):
                            self.logger.error("Model %s has no _meta", name)
                            continue
                        if getattr(model._meta, "db_table", None) != name:
                            self.logger.error("Table name mismatch")
                            continue
                        break
                if not model:
                    self.logger.error("Model not found: %s", name)
                self.models[name] = model
            return model

    def is_valid_name(self, name):
        return ".." not in name

    def iter_models(self):
        with self.lock:
            if not self.all_models:
                self.all_models = self.find_models()
        for ds in sorted(self.all_models):
            yield ds

    def find_models(self):
        """
        Scan all available models
        """
        names = set()
        for dn in config.get_customized_paths(os.path.join("bi", "models")):
            for file in os.listdir(dn):
                if file.startswith("_") or not file.endswith(".py"):
                    continue
                name = file[:-3]
                if name not in self.IGNORED_MODELS:
                    names.add(file[:-3])
        return names


# Create singleton object
loader = ModelLoader()
