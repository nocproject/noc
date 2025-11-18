# ---------------------------------------------------------------------
# Base dynamic dashboard
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from importlib.resources import files
from importlib.resources.abc import Traversable
import logging

# Third-Party modules
import orjson

BAD_CHARS = "!\"%'()+,:;<>?@^`{|}~\\\n\r"


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

        def load_file(file: Traversable):
            if file.suffix == ".json":
                with file.open() as data_file:
                    try:
                        t[file.name.split(".")[0]] = orjson.loads(data_file.read())
                    except ValueError:
                        self.logger.error(
                            f"Dashboard template file '{file}' not contains valid JSON"
                        )
            else:
                self.logger.info(f"Extension file '{file}' is not .json")

        for prefix in ("noc.custom", "noc"):
            t_path = self.templates_path or "services.web.apps.pm.ddash.dashboards.templates"
            pkg: str = f"{prefix}.{t_path}"
            try:
                templates_dir: Traversable = files(pkg)
            except ModuleNotFoundError:
                self.logger.warning(f"Templates path '{pkg}' is not exist")
                continue
            t = {}
            for f in templates_dir.iterdir():
                if f.is_file():
                    load_file(f)
                elif f.is_dir():
                    for fl in f.iterdir():
                        if fl.is_file():
                            load_file(fl)
            return t
        return {}

    def str_cleanup(self, data, remove_letters=None, translate_to=None):
        if data:
            remove_letters = remove_letters or BAD_CHARS
            translate_table = {ord(char): translate_to for char in remove_letters}
            return data.translate(translate_table)
        else:
            return data
