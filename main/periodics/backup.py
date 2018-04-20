# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Backup database,  repo and configs to main.backupdir
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
=======
##----------------------------------------------------------------------
## Backup database,  repo and configs to main.backupdir
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from __future__ import with_statement
import os
import subprocess
import datetime
import re
import shutil
<<<<<<< HEAD
# NOC modules
from noc.lib.periodic import Task as PeriodicTask
from noc.settings import config
from noc import settings
from noc.core.fileutils import safe_rewrite
from noc.config import config
=======
## NOC modules
from noc.lib.periodic import Task as PeriodicTask
from noc.settings import config
from noc import settings
from noc.lib.fileutils import safe_rewrite
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce


class Task(PeriodicTask):
    name = "main.backup"
    description = ""

    def check_paths(self):
        """
        Verify all executables and directories are exists
        """
        self.info("Checking paths")
        # Check backup dir is writable
<<<<<<< HEAD
        b_dir = config.path.backup_dir
=======
        b_dir = config.get("path", "backup_dir")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        if not os.access(b_dir, os.W_OK):
            self.error("%s is not writable" % b_dir)
            return False
        # Check binaries
        for p in ("pg_dump", "mongodump", "tar", "gzip"):
            path = config.get("path", p)
            if not os.path.exists(path):
                self.error("%s is not found" % path)
                return False
            if not os.access(path, os.R_OK | os.X_OK):
                self.error("Permission denied: %s" % path)
        return True

    rx_backup = re.compile(r"^noc-(?:(?:etc|repo|db|mongo)-)(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})-\d{2}-\d{2}.(?:dump|tar\.gz)$")

    def clean_backups(self):
        """
        Cleanup obsolete backups
        """
<<<<<<< HEAD
        backup_dir = config.path.backup_dir
        keep_days = config.backup.keep_days
        keep_weeks = config.backup.keep_weeks
        keep_day_of_week = config.backup.keep_day_of_week
        keep_months = config.backup.keep_months
        keep_day_of_month = config.backup.keep_day_of_month
=======
        backup_dir = config.get("path", "backup_dir")
        keep_days = config.getint("backup", "keep_days")
        keep_weeks = config.getint("backup", "keep_weeks")
        keep_day_of_week = config.getint("backup", "keep_day_of_week")
        keep_months = config.getint("backup", "keep_months")
        keep_day_of_month = config.getint("backup", "keep_day_of_month")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

        now = datetime.datetime.now()
        if not os.path.isdir(backup_dir):
            self.error("No backup directory: %s" % backup_dir)
            return
        for f in os.listdir(backup_dir):
            match = self.rx_backup.match(f)
            if not match:
                continue
            try:
                bdate = datetime.datetime(year=int(match.group("year")),
                                          month=int(match.group("month")),
                                          day=int(match.group("day")))
            except:
                continue
            # Filter out actual backups
            delta = now - bdate
            if delta.days < keep_days:
                continue
            elif delta.days < keep_days + keep_weeks * 7:
                if (bdate.weekday() == keep_day_of_week or
                            bdate.day == keep_day_of_month):
                    continue
            elif (delta.days < keep_days + keep_weeks * 7 + keep_months * 31):
                if bdate.day == keep_day_of_month:
                    continue
            # Remove deprecated backups
            self.info("Removing obsolete backup %s" % f)
            self.safe_unlink(os.path.join(backup_dir, f))

    def safe_unlink(self, path):
        """
        Safely remove file
        """
        self.debug("Unlinking: %s" % path)
        if os.path.isdir(path):
            try:
                shutil.rmtree(path)
            except:
                pass
        else:
            try:
                os.unlink(path)
            except:
                pass

    def subprocess_call(self, cmd, env=None):
        try:
            return subprocess.call(cmd, env=env)
<<<<<<< HEAD
        except OSError as why:
=======
        except OSError, why:
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            self.error("Failed to call '%s': %s" % (cmd, why))
            return -1

    def tar(self, archive, files, cwd=None):
        """
        Create TAR archive
        """
        if not files:
            return
        tar_cmd = [config.get("path", "tar"), "cf", "-"] + files
        gzip_cmd = [config.get("path", "gzip")]
        self.debug(("cd %s &&" % cwd if cwd else ".") + " ".join(tar_cmd) +
            " | " + " ".join(gzip_cmd))
        with open(archive, "w") as f:
            try:
                p1 = subprocess.Popen(tar_cmd, cwd=cwd, stdout=subprocess.PIPE)
                p2 = subprocess.Popen(gzip_cmd, stdin=p1.stdout, stdout=f)
<<<<<<< HEAD
            except OSError as why:
=======
            except OSError, why:
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                self.error("Failed to tar: %s" % why)
                return False
            return p2.wait() == 0

    def backup_postgres(self):
        """
        Backup postgresql database
        """
        def pgpass_quote(s):
            return s.replace("\\", "\\\\").replace(":", "\\:")

        now = datetime.datetime.now()
<<<<<<< HEAD
        # host, port, database, user, password
        pgpass = ["*", "*", "*", "*", ""]
        out = "noc-db-%04d-%02d-%02d-%02d-%02d.dump" % (
            now.year, now.month, now.day, now.hour, now.minute)
=======
        pgpass = ["*", "*", "*", "*", ""]  # host, port, database, user, password
        out = "noc-db-%04d-%02d-%02d-%02d-%02d.dump" % (now.year, now.month,
                                                        now.day, now.hour,
                                                        now.minute)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        out = os.path.join(config.get("path", "backup_dir"), out)
        # Build pg_dump command and options
        cmd = [config.get("path", "pg_dump"), "-Fc"]
        cmd += ["-f", out]
<<<<<<< HEAD
        if config.pg.user:
            cmd += ["-U", config.pg.user]
            pgpass[3] = config.pg.user
        if config.pg.password:
            pgpass[4] = config.pg.password
        cmd += ["-h", config.pg_connection_args["host"]]
        pgpass[0] = config.pg_connection_args["host"]
        if config.pg_connection_args["port"]:
            cmd += ["-p", str(config.pg_connection_args["port"])]
            pgpass[1] = config.pg_connection_args["port"]
=======
        if settings.DATABASES["default"]["USER"]:
            cmd += ["-U", settings.DATABASES["default"]["USER"]]
            pgpass[3] = settings.DATABASES["default"]["USER"]
        if settings.DATABASES["default"]["PASSWORD"]:
            pgpass[4] = settings.DATABASES["default"]["PASSWORD"]
        if settings.DATABASES["default"]["HOST"]:
            cmd += ["-h", settings.DATABASES["default"]["HOST"]]
            pgpass[0] = settings.DATABASES["default"]["HOST"]
        if settings.DATABASES["default"]["PORT"]:
            cmd += ["-p", str(settings.DATABASES["default"]["PORT"])]
            pgpass[1] = settings.DATABASES["default"]["PORT"]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        cmd += [settings.DATABASES["default"]["NAME"]]
        pgpass[2] = settings.DATABASES["default"]["NAME"]
        # Create temporary .pgpass
        pgpass_data = ":".join([pgpass_quote(x) for x in pgpass])
        pgpass_path = os.path.join(os.getcwd(), "local", "cache", "pgpass", ".pgpass")
<<<<<<< HEAD
        safe_rewrite(pgpass_path, pgpass_data, mode=0o600)
=======
        safe_rewrite(pgpass_path, pgpass_data, mode=0600)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        env = os.environ.copy()
        env["PGPASSFILE"] = pgpass_path
        # Launch pg_dump
        self.info("Dumping PostgreSQL database into %s" % out)
        self.debug(" ".join(cmd))
        retcode = self.subprocess_call(cmd, env=env)
        if retcode != 0:
            self.error("dump failed. Removing broken dump %s" % out)
            self.safe_unlink(out)
            return False
        self.safe_unlink(pgpass_path)  # Remove left pgpass
        return True

    def backup_mongo(self):
        """
        Backup mongodb database
        """
        now = datetime.datetime.now()
<<<<<<< HEAD
        f_out = "noc-mongo-%04d-%02d-%02d-%02d-%02d" % (
            now.year, now.month, now.day, now.hour, now.minute)
        out = os.path.join(config.get("path", "backup_dir"), f_out)
        try:
            os.mkdir(out)
        except OSError as e:
            self.error("Cannot create directory %s: %s" % (out, why))
            return False
        cmd = [config.get("path", "mongodump"),
               "-d", config.mongo.db,
               "-o", out,
               "-h", config.mongo_connection_args["url"]]
        if config.mongo.user:
            cmd += ["-u", config.mongo.user]
        if config.mongo.password:
            cmd += ["-p", config.mongo.password]
=======
        f_out = "noc-mongo-%04d-%02d-%02d-%02d-%02d" % (now.year, now.month,
                                                        now.day, now.hour,
                                                        now.minute)
        out = os.path.join(config.get("path", "backup_dir"), f_out)
        try:
            os.mkdir(out)
        except OSError, why:
            self.error("Cannot create directory %s: %s" % (out, why))
            return False
        cmd = [config.get("path", "mongodump"),
               "-d", settings.NOSQL_DATABASE_NAME,
               "-o", out]
        if settings.NOSQL_DATABASE_HOST:
            cmd += ["-h", settings.NOSQL_DATABASE_HOST]
        if settings.NOSQL_DATABASE_PORT:
            cmd += ["--port", settings.NOSQL_DATABASE_PORT]
        if settings.NOSQL_DATABASE_USER:
            cmd += ["-u", settings.NOSQL_DATABASE_USER]
        if settings.NOSQL_DATABASE_PASSWORD:
            cmd += ["-p", settings.NOSQL_DATABASE_PASSWORD]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        self.info("Dumping MongoDB database into %s" % out)
        retcode = self.subprocess_call(cmd)
        if retcode:
            self.error("dump failed. Removing broken dump %s" % out)
            self.safe_unlink(out)
            return False
        self.info("Archiving dump")
<<<<<<< HEAD
        r = self.tar(out + ".tar.gz", [config.mongo.db], cwd=out)
=======
        r = self.tar(out + ".tar.gz", [settings.NOSQL_DATABASE_NAME], cwd=out)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        self.safe_unlink(out)
        return r

    def backup_repo(self):
        """
        Backup repo
        """
        now = datetime.datetime.now()
        repo_root = config.get("cm", "repo")
        repo_out = "noc-repo-%04d-%02d-%02d-%02d-%02d.tar.gz" % (now.year,
                                    now.month, now.day, now.hour, now.minute)
        repo_out = os.path.join(config.get("path", "backup_dir"), repo_out)
        self.info("dumping repo into %s" % repo_out)
        self.tar(repo_out, [f for f in os.listdir(repo_root)
                            if not f.startswith(".")], cwd=repo_root)
        return True

    def backup_etc(self):
        """
        Backup etc/
        """
        now = datetime.datetime.now()
        etc_out = "noc-etc-%04d-%02d-%02d-%02d-%02d.tar.gz" % (now.year,
                                    now.month, now.day, now.hour, now.minute)
        etc_out = os.path.join(config.get("path", "backup_dir"), etc_out)
        self.info("dumping etc/ into %s" % etc_out)
        try:
            files = [os.path.join("etc", f) for f in os.listdir("etc")
                     if f.endswith(".conf") and not f.startswith(".")]
            files += [os.path.join("etc", "ssh", f)
                      for f in os.listdir(os.path.join("etc", "ssh"))
                      if not f.startswith(".")]
<<<<<<< HEAD
        except OSError as why:
=======
        except OSError, why:
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            self.error("Failed to get list of files: %s" % why)
            return False
        return self.tar(etc_out, files)

    def execute(self):
        from django.conf import settings

        if not self.check_paths():
            return False
        self.clean_backups()
        r = True
        r &= self.backup_postgres()
        r &= self.backup_mongo()
        r &= self.backup_repo()
        r &= self.backup_etc()
        return r
