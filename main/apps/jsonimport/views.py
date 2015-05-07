# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.jsonimport application
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtApplication, view
from noc.lib.serialize import json_decode
from noc.sa.interfaces.base import StringParameter
from noc.lib.collection import Collection


class JSONImportApplication(ExtApplication):
    """
    main.jsonimport application
    """
    title = "JSON Import"
    menu = "Setup | JSON Import"

    @view(url="^$", method=["POST"], access="launch",
          validate={
              "json": StringParameter(required=True)
          },
          api=True)
    def api_import(self, request, json):
        try:
            jdata = json_decode(json)
        except Exception, why:
            return {
                "status": False,
                "error": "Invalid JSON: %s" % why
            }
        try:
            if isinstance(jdata, list):
                for d in jdata:
                    self.import_object(d)
            else:
                self.import_object(jdata)
        except ValueError, why:
            return {
                "status": False,
                "error": str(why)
            }
        return {
            "status": True
        }

    def import_object(self, obj):
        collection = obj.get("$collection")
        if not collection:
            raise ValueError("No $collection attribute")
        c = Collection(collection, local=True)  # Can raise ValueError
        c.install_item(obj, load=True)
        # Do not save
