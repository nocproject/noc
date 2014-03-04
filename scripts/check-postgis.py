#!./bin/python
##----------------------------------------------------------------------
## Check PostGIS installation
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##---------------------------------------------------------------------

## Python modules
import sys
import os
import subprocess
import glob
## Third-party modules
import psycopg2
## NOC modules
from settings import config
from noc.lib.fileutils import safe_rewrite


class PGDriver(object):
    # Compatible versions
    POSTGIS_VERSIONS = ["2.1", "2.0", "1.5"]
    POSTGIS_FILES = ["postgis.sql", "spatial_ref_sys.sql",
                     "postgis_comments.sql",
                     "rtpostgis.sql",
                     "topology/topology.sql", "topology.sql",
                     "topology/topology_comments.sql",
                     "topology_comments.sql",
                     "legacy.sql", "legacy_gist.sql",
                     "raster_comments.sql"]

    REQUIRED_POSTGIS_FILES = ["postgis.sql", "spatial_ref_sys.sql"]

    def __init__(self):
        pass

    def check(self):
        self.pgpass_path = None
        # Check for postgis
        self.info("Checking PostGIS installation")
        self.setup_credentials()
        if self.check_postgis():
            self.info("   ... found")
            sys.exit(0)
        # Install postgis
        self.info("   ... not found")
        self.info("Installing postgis")
        self.pg_sharedir = self.pg_config("--sharedir")
        self.assert_dir(self.pg_sharedir)
        self.pg_contrib = os.path.join(self.pg_sharedir, "contrib")
        self.assert_dir(self.pg_contrib)
        self.pg_bindir = self.pg_config("--bindir")
        self.psql_path = os.path.join(self.pg_bindir, "psql")
        self.assert_file(self.psql_path)
        self.install_postgis()

    def pg_config(self, *args):
        try:
            p = subprocess.Popen(
                ["pg_config"] + list(args),
                stdout=subprocess.PIPE
            )
            return p.stdout.read().strip()
        except OSError:
            pass

    def psql_in(self, path):
        self.info("    ... installing %s" % path)
        args = [self.psql_path, "-q"]
        if self.db_cred.get("user"):
            args += ["-U", self.db_cred["user"]]
        args += ["-w", "-f", path, self.db_cred["database"]]
        env = os.environ.copy()
        env["PGPASSFILE"] = self.pgpass_path
        try:
            subprocess.check_call(args, env=env)
        except OSError:
            self.fail("Failed to install %s" % path)

    def assert_dir(self, path):
        if not os.path.isdir(path):
            self.fail("Directory %s does not exist" % path)

    def assert_file(self, path):
        if not os.path.isfile(path):
            self.fail("Cannot read file %s" % path)

    def info(self, msg):
        print msg

    def fail(self, msg):
        sys.stderr.write("ERROR: %s\n" % msg)
        self.destroy_pgpass()
        sys.exit(1)

    def setup_credentials(self):
        def update(d, kw, k=None):
            k = k or kw
            v = config.get("database", k)
            if v:
                d[kw] = v

        self.db_cred = {
            "database": config.get("database", "name")
        }
        update(self.db_cred, "user")
        update(self.db_cred, "password")
        update(self.db_cred, "host")
        update(self.db_cred, "port")

    def check_postgis(self):
        cn = psycopg2.connect(**self.db_cred)
        c = cn.cursor()
        c.execute("SELECT COUNT(*) FROM pg_class WHERE relname='geometry_columns'")
        return c.fetchall()[0][0] == 1

    def get_postgis_prefix(self):
        """
        Returns (postgis version, postgis prefix)
        """
        u = os.uname()
        if u[0] == "FreeBSD":
            fp = "/usr/local/share/postgis/contrib/"
            if os.path.isdir(fp):
                base = fp
            else:
                base = self.pg_contrib
        else:
            base = self.pg_contrib
        self.assert_dir(base)
        paths = glob.glob(os.path.join(base, "postgis-*"))
        for pv in self.POSTGIS_VERSIONS:
            for p in paths:
                f = os.path.basename(p)
                if f.endswith(pv):
                    return pv, p
        self.fail("PostGIS installation not found")

    def prepare_pgpass(self):
        def q(s):
            return s.replace("\\", "\\\\").replace(":", "\\:")

        self.pgpass_path = os.path.join(
            os.getcwd(), "local", "cache", "pgpass", ".pgpass")
        pgpass = ["*", "*", "*", "*", ""]
        for i, c in enumerate(["host", "port", "database", "user", "password"]):
            if self.db_cred.get(c):
                pgpass[i] = q(self.db_cred[c])
        # Create temporary .pgpass
        pgpass_data = ":".join(pgpass)
        safe_rewrite(self.pgpass_path, pgpass_data)

    def destroy_pgpass(self):
        if self.pgpass_path and os.path.isfile(self.pgpass_path):
            os.unlink(self.pgpass_path)
            self.pgpass_path = None

    def install_postgis(self):
        pv, prefix = self.get_postgis_prefix()
        # Build install bundle
        install = []
        for f in self.POSTGIS_FILES:
            path = os.path.join(prefix, f)
            if os.path.isfile(path):
                install += [path]
            elif os.path.basename(f) in self.REQUIRED_POSTGIS_FILES:
                self.fail("Required file %s is not found" % f)
        # Install files
        self.prepare_pgpass()
        for p in install:
            self.psql_in(p)
        self.destroy_pgpass()
        self.info("   ... done")

if __name__ == "__main__":
    PGDriver().check()
