# ---------------------------------------------------------------------
# Jinja dynamic dashboard
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os

# Third-party modules
from jinja2 import Environment, FileSystemLoader
import demjson3

# NOC modules
from noc.config import config
from .base import BaseDashboard


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
        self.logger.info("Context with data: %s" % context)
        pm_template_path = []
        for p in config.get_customized_paths("", prefer_custom=True):
            if p:
                pm_template_path += [os.path.join(p, "templates/ddash/")]
            else:
                pm_template_path += [config.path.pm_templates]
        j2_env = Environment(loader=FileSystemLoader(pm_template_path))
        j2_env.globals["noc_db_metrics"] = config.clickhouse.db
        tmpl = j2_env.get_template(self.template)
        data = tmpl.render(context)
        return demjson3.decode(data)
