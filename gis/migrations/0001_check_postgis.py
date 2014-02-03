# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

import sys
import os
import subprocess
from noc.lib.db import *
from noc.settings import config
from noc import settings
from noc.lib.fileutils import safe_rewrite


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
        def pgpass_quote(s):
            return s.replace("\\", "\\\\").replace(":", "\\:")

        if not os.path.exists(path):
            self.fail("File not found: %s" % path)
        if not hasattr(self, "psql"):
            bindir = pg_bindir() or ""
            self.psql = os.path.join(bindir, "psql")
        # Prepare pgpass file
        pgpass = ["*", "*", "*", "*", ""]
        if settings.DATABASES["default"]["USER"]:
            pgpass[3] = settings.DATABASES["default"]["USER"]
        if settings.DATABASES["default"]["PASSWORD"]:
            pgpass[4] = settings.DATABASES["default"]["PASSWORD"]
        if settings.DATABASES["default"]["HOST"]:
            pgpass[0] = settings.DATABASES["default"]["HOST"]
        if settings.DATABASES["default"]["PORT"]:
            pgpass[1] = settings.DATABASES["default"]["PORT"]
        pgpass[2] = settings.DATABASES["default"]["NAME"]
        # Create temporary .pgpass
        pgpass_data = ":".join([pgpass_quote(x) for x in pgpass])
        pgpass_path = os.path.join(os.getcwd(), "local", "cache", "pgpass", ".pgpass")
        safe_rewrite(pgpass_path, pgpass_data, mode=0600)
        print "Executing: %s" % path
        env = os.environ.copy()
        env["PGPASSFILE"] = pgpass_path
        try:
            subprocess.check_call([
                self.psql,
                "-f", path,
                "-U", config.get("database", "user"),
                "-w",
                config.get("database", "name")
            ], env=env)
        except OSError:
            self.fail("psql binary not found at: %s" % self.psql)
        finally:
            try:
                os.unlink(pgpass_data)
            except:
                pass

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
            legacy_gist = os.path.join(self.get_postgis_root(),
                                       "legacy_gist.sql")
            if os.path.exists(legacy_gist):
                self.exec_file(legacy_gist)
        if not check_srs():
            print "Trying to install spatial_ref_sys"
            self.exec_file(os.path.join(self.get_postgis_root(),
                           "spatial_ref_sys.sql"))

    def backwards(self):
        pass
