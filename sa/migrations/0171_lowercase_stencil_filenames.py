# -*- coding: utf-8 -*-

from south.db import db


class Migration:

    def forwards(self):
        db.execute("""update sa_managedobjectprofile set shape=upper(substring(shape from 1 for 1))||lower(substring(shape from 2 for length(shape)))""")
        db.execute("""update sa_managedobject set shape=upper(substring(shape from 1 for 1))||lower(substring(shape from 2 for length(shape)))""")

    def backwards(self):
        pass
