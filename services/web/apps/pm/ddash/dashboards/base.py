# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Base dynamic dashboard
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import ujson
import logging


class BaseDashboard(object):
    name = None

    class NotFound(Exception):
        pass

    def __init__(self, object):
        self.object = self.resolve_object(object)
        self.logger = logging.getLogger("dashboard.%s" % self.name)
        self.object_data = self.resolve_object_data(object)
        self.templates_path = ""
        self.templates = self.load_templates()

    def resolve_object(self, object):
        """
        Resolve symbolic object link to name
        """
        return object

    def resolve_object_data(self, object):
        """
        Return Dictionary with data for grafana templating section
        """
        return {}

    def render(self):
        """
        Render dashboard and return grafana's dashboard JSON
        """
        return None

    def load_templates(self):
        """
        Load dashboard templates from path and return template dict, key is folder.filename without .json
        """
        if self.templates_path:
            t_path = self.templates_path
        else:
            t_path = os.path.join("services", "web", "apps", "pm", "ddash", "dashboards", "templates")
        t = {}
        if not os.path.exists(t_path):
            self.logger.warn("Templates path %s is not exist" % t_path)
            return {}
        for f in os.listdir(t_path):
            path = os.path.join(t_path, f)
            if os.path.isfile(path):
                if ".json" not in f:
                    self.logger.info("Extension file %s is not .json" % fl)
                    continue
                with open(os.path.join(t_path, f)) as data_file:
                    try:
                        t[f.split(".")[0]] = ujson.load(data_file)
                    except ValueError:
                        self.logger.error("Dashboard template file %s not contains valid JSON" % fl)
                        continue
                continue
            for fl in os.listdir(path):
                if ".json" not in fl:
                    self.logger.info("Extension file %s is not .json" % fl)
                    continue
                with open(os.path.join(t_path, f, fl)) as data_file:
                    try:
                        t[".".join((f, fl.split(".")[0]))] = ujson.load(data_file)
                    except ValueError:
                        self.logger.error("Dashboard template file %s not contains valid JSON" % fl)
                        continue
        return t
