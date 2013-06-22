# -*- coding: utf-8 -*-
from noc.lib.nosql import get_db


class Migration:
    def forwards(self):
        c = get_db().noc.pm.ts
        info = c.index_information()
        for name in info:
            if info[name]["key"] == [(u"name", 1)]:
                c.drop_index(name)

    def backwards(self):
        pass