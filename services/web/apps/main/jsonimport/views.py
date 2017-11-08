# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# main.jsonimport application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import ujson
from noc.core.collection.base import Collection
from noc.core.translation import ugettext as _
# NOC modules
from noc.lib.app.extapplication import ExtApplication, view
from noc.sa.interfaces.base import StringParameter


class JSONImportApplication(ExtApplication):
    """
    main.jsonimport application
    """
    title = _("JSON Import")
    menu = [_("Setup"), _("JSON Import")]

    @view(url="^$", method=["POST"], access="launch",
          validate={
              "json": StringParameter(required=True)
          },
          api=True)
    def api_import(self, request, json):
        try:
            jdata = ujson.loads(json)
        except Exception as e:
            return {
                "status": False,
                "error": "Invalid JSON: %s" % e
            }
        try:
            if isinstance(jdata, list):
                for d in jdata:
                    Collection.install(d)
                    c = Collection(d["$collection"])
                    c.update_item(d)
            else:
                Collection.install(jdata)
                c = Collection(jdata["$collection"])
                c.update_item(jdata)
        except ValueError as e:
            return {
                "status": False,
                "error": str(e)
            }
        return {
            "status": True
        }
