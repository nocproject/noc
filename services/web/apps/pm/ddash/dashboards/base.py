# ---------------------------------------------------------------------
# Base dynamic dashboard
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from importlib.resources import files
import logging
import os

# Third-Party modules
import orjson

BAD_CHARS = r"!\"%'()+,:;<>?@\^`{|}~\\\n\r"


class BaseDashboard(object):
    name = None

    class NotFound(Exception):
        pass

    def __init__(self, object, extra_template=None, extra_vars=None):
        self.object = self.resolve_object(object)
        self.extra_template = extra_template
        self.extra_vars = extra_vars
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
            t_path = os.path.join(
                "services", "web", "apps", "pm", "ddash", "dashboards", "templates"
            )
        t = {}
        if not os.path.exists(t_path):
            self.logger.warning("Templates path %s is not exist" % t_path)
            return {}
        for f in os.listdir(t_path):
            path = os.path.join(t_path, f)
            if os.path.isfile(path):
                if ".json" not in f:
                    self.logger.info("Extension file %s is not .json" % f)
                    continue
                with files("noc").joinpath(t_path, f).open() as data_file:
                    try:
                        t[f.split(".")[0]] = orjson.loads(data_file.read())
                    except ValueError:
                        self.logger.error("Dashboard template file %s not contains valid JSON" % f)
                        continue
                continue
            for fl in os.listdir(path):
                if ".json" not in fl:
                    self.logger.info("Extension file %s is not .json" % fl)
                    continue
                with files("noc").joinpath(t_path, f, fl).open() as data_file:
                    try:
                        t[".".join((f, fl.split(".")[0]))] = orjson.loads(data_file.read())
                    except ValueError:
                        self.logger.error("Dashboard template file %s not contains valid JSON" % fl)
                        continue
        return t

    def str_cleanup(self, data, remove_letters=None, translate_to=None):
        if data:
            remove_letters = remove_letters or BAD_CHARS
            translate_table = {ord(char): translate_to for char in remove_letters}
            return data.translate(translate_table)
        else:
            return data
