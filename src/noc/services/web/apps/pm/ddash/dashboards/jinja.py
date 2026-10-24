# ---------------------------------------------------------------------
# Jinja dynamic dashboard
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from contextlib import ExitStack
from importlib.resources import as_file, files
from pathlib import Path

# Third-party modules
from jinja2 import Environment, FileSystemLoader
import demjson3

# NOC modules
from noc.config import config
from .base import BaseDashboard

PM_TEMPLATES = files("noc.services.web.apps.pm.ddash").joinpath("templates")


class JinjaDashboard(BaseDashboard):
    template = None

    def get_context(self):
        """
        Context for render template
        :return:
        """
        return {}

    def render(self):
        context = self.get_context()
        self.logger.info(f"Context with data: {context}")
        template_paths = []
        for p in config.get_customized_paths(prefer_custom=True):
            if not p:
                continue
            custom_templates = Path(p) / "services" / "web" / "apps" / "pm" / "ddash" / "templates"
            if custom_templates.is_dir():
                template_paths.append(str(custom_templates))
        with ExitStack() as stack:
            template_paths.append(str(stack.enter_context(as_file(PM_TEMPLATES))))
            j2_env = Environment(loader=FileSystemLoader(template_paths))
            j2_env.globals["noc_db_metrics"] = config.clickhouse.db
            tmpl = j2_env.get_template(self.template)
            data = tmpl.render(context)
        return demjson3.decode(data)
