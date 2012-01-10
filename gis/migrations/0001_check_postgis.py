# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from __future__ import with_statement
import sys
import os
from django.db import connection
from south.db import db
from noc.lib.db import *

class Migration:
    def fail(self):
        print "Failed to install PostGIS"
        print "Install PostGIS according to your operation system procedure"
        print "Stopping..."
        sys.exit(1)

    def exec_file(self, path):
        if not os.path.exists(path):
            print "File not found: %s" % path
            self.fail()
        c = connection.cursor()
        with open(path) as f:
            sql = f.read().replace("%", "%%")
        print "Executing: %s" % path
        c.execute(sql)

    def forwards(self):
        if not check_postgis():
            print "PostGIS is not installed. Trying to install ..."
            sd = pg_sharedir()
            if not sd:
                self.fail()
            self.exec_file(os.path.join(sd, "contrib", "postgis-1.5",
                                       "postgis.sql"))
            comments = os.path.join(sd, "contrib", "postgis-1.5",
                                    "postgis_comments.sql")
            if os.path.exists(comments):
                self.exec_file(comments)
        if not check_srs():
            print "Trying to install spatial_ref_sys"
            self.exec_file(os.path.join(sd, "contrib", "postgis-1.5",
                                       "spatial_ref_sys.sql"))





    def backwards(self):
        pass