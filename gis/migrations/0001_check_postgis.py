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
    def fail(self, msg=None):
        if msg:
            print "Failed to install PostGIS: %s" % msg
        else:
            print "Failed to install PostGIS."
        print "Install PostGIS according to your operation system procedure"
        print "Stopping..."
        sys.exit(1)

    def exec_file(self, path):
        if not os.path.exists(path):
            self.fail("File not found: %s" % path)
        c = connection.cursor()
        with open(path) as f:
            sql = f.read().replace("%", "%%")
        print "Executing: %s" % path
        c.execute(sql)

    def get_postgis_root(self):
        """
        Get PostGIS SQL scripts directory
        :return:
        """
        # Use cached value
        try:
            return self.posgis_root
        except AttributeError:
            pass
        #
        root = None
        # OS-depended hardcoded paths
        u = os.uname()
        if u[0] == "FreeBSD":
            root = "/usr/local/share/postgis/contrib/postgis-1.5"
        # Check hardcoded path exists
        if root and os.path.exists(root):
            self.postgis_root = root
            return root
        # Try $PGSHARE/contrib/postgis-1.5
        sd = pg_sharedir()
        if not sd:
            self.fail("pg_config is not found")
        root = os.path.join(sd, "contrib", "postgis-1.5")
        if not os.path.exists(root):
            self.fail("Not found: %s" % root)
        self.postgis_root = root
        return root

    def forwards(self):
        if not check_postgis():
            print "PostGIS is not installed. Trying to install ..."
            self.exec_file(os.path.join(self.get_postgis_root(),
                                        "postgis.sql"))
            comments = os.path.join(self.get_postgis_root(),
                                    "postgis_comments.sql")
            if os.path.exists(comments):
                self.exec_file(comments)
        if not check_srs():
            print "Trying to install spatial_ref_sys"
            self.exec_file(os.path.join(self.get_postgis_root(),
                           "spatial_ref_sys.sql"))

    def backwards(self):
        pass