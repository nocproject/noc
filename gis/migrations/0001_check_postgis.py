# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from __future__ import with_statement
import sys
import os
from south.db import db
from noc.lib.db import *
from noc.settings import config


class Migration:
    def fail(self, msg=None):
        if msg:
            print "Failed to install PostGIS: %s" % msg
        else:
            print "Failed to install PostGIS."
        dbname = config.get("database", "name")
        print "Install PostGIS into database '%s' according to your operation system's procedure" % dbname
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
            for v in ["2.1", "2.0", "1.5"]:
                root = "/usr/local/share/postgis/contrib/postgis-%s" % v
                if os.path.exists(root):
                    self.postgis_root = root
                    return root
        elif u[0] == "SunOS":
            pass
        # Check hardcoded path exists
        if root and os.path.exists(root):
            self.postgis_root = root
            return root
        # Try $PGSHARE/contrib/postgis-1.5
        sd = pg_sharedir()
        if not sd:
            self.fail("pg_config is not found.\n"\
                      "Ensure pg_config is in the current user's $PATH")
        for v in ["2.1", "2.0", "1.5"]:
            root = os.path.join(sd, "contrib", "postgis-%s" % v)
            if os.path.exists(root):
                self.postgis_root = root
                return root
        self.fail("Not found: %s" % root)

    def forwards(self):
        if not check_postgis():
            print "PostGIS is not installed. Trying to install ..."
            if not check_pg_superuser():
                # Superuser required
                dbname = config.get("database", "name")
                dbuser = config.get("database", "user")
                print "PostgreSQL superuser permissions required to install PostGIS"
                print "Temporary grant superuser permissions to '%s'" % dbuser
                print "Or install PostGIS into database '%s' manually" % dbname
                sys.exit(1)
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
