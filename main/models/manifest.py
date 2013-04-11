## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Manifest model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.nosql import Document, StringField
from noc.lib.updateclient import UpdateClient


class Manifest(Document):
    meta = {
        "collection": "noc.manifest",
        "allow_inheritance": False,
        "indexes": ["name"]
    }

    name = StringField()
    path = StringField()
    hash = StringField()

    def unicode(self):
        return "%s:%s" % (self.name, self.path)

    @classmethod
    def get_manifest(cls, name):
        """
        Return dict of path -> hash
        :return:
        """
        return dict((m["path"], m["hash"])
                    for m in cls._get_collection().find({"name": name}))

    @classmethod
    def update_manifest(cls, name):
        uc = UpdateClient("", names=[name])
        c = cls._get_collection()
        c.remove({"name": name})
        c.insert([
            {
                "name": name,
                "path": path,
                "hash": uc.manifest[path]
            } for path in uc.manifest])
