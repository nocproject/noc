# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Backup database,  repo and configs to main.backupdir
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import os
import subprocess
import datetime
import re
import shutil
## NOC modules
from noc.lib.periodic import Task as PeriodicTask
from noc.settings import config
from noc import settings
from noc.lib.fileutils import safe_rewrite


class Task(PeriodicTask):
    name = "main.backup"
    description = ""

    def check_paths(self):
        """
        Verify all executables and directories are exists
        """
        self.info("Checking paths")
        # Check backup dir is writable
        b_dir = config.get("path", "backup_dir")
        if not os.access(b_dir, os.W_OK):
            self.error("%s is not writable" % b_dir)
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
        backup_dir = config.get("path", "backup_dir")
        keep_days = config.getint("backup", "keep_days")
        keep_weeks = config.getint("backup", "keep_weeks")
        keep_day_of_week = config.getint("backup", "keep_day_of_week")
        keep_months = config.getint("backup", "keep_months")
        keep_day_of_month = config.getint("backup", "keep_day_of_month")

        now = datetime.datetime.now()
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

    def tar(self, archive, files, cwd=None):
        """
        Create TAR archive
        """
        if not files:
            return
        tar_cmd = [config.get("path", "tar"), "cf", "-"] + files
        gzip_cmd = [config.get("path", "gzip")]
        self.debug(("cd %s &&" % cwd if cwd else "") + " ".join(tar_cmd) +
            " | " + " ".join(gzip_cmd))
        with open(archive, "w") as f:
            p1 = subprocess.Popen(tar_cmd, cwd=cwd, stdout=subprocess.PIPE)
            p2 = subprocess.Popen(gzip_cmd, stdin=p1.stdout, stdout=f)
            return p2.wait() == 0

    def backup_postgres(self):
        """
        Backup postgresql database
        """
        def pgpass_quote(s):
            return s.replace("\\", "\\\\").replace(":", "\\:")

        now = datetime.datetime.now()
        pgpass = ["*", "*", "*", "*", ""]  # host, port, database, user, password
        out = "noc-db-%04d-%02d-%02d-%02d-%02d.dump" % (now.year, now.month,
                                                        now.day, now.hour,
                                                        now.minute)
        out = os.path.join(config.get("path", "backup_dir"), out)
        # Build pg_dump command and options
        cmd = [config.get("path", "pg_dump"), "-Fc"]
        cmd += ["-f", out]
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
        cmd += [settings.DATABASES["default"]["NAME"]]
        pgpass[2] = settings.DATABASES["default"]["NAME"]
        # Create temporary .pgpass
        pgpass_data = ":".join([pgpass_quote(x) for x in pgpass])
        pgpass_path = os.path.join(os.getcwd(), "local", "cache", "pgpass", ".pgpass")
        safe_rewrite(pgpass_path, pgpass_data, mode=0600)
        env = os.environ.copy()
        env["PGPASSFILE"] = pgpass_path
        # Launch pg_dump
        self.info("Dumping PostgreSQL database into %s" % out)
        self.debug(" ".join(cmd))
        retcode = subprocess.call(cmd, env=env)
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
        f_out = "noc-mongo-%04d-%02d-%02d-%02d-%02d" % (now.year, now.month,
                                                        now.day, now.hour,
                                                        now.minute)
        out = os.path.join(config.get("path", "backup_dir"), f_out)
        os.mkdir(out)
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
        self.info("Dumping MongoDB database into %s" % out)
        retcode = subprocess.call(cmd)
        if retcode:
            self.error("dump failed. Removing broken dump %s" % out)
            self.safe_unlink(out)
            return False
        self.info("Archiving dump")
        self.tar(out + ".tar.gz", [settings.NOSQL_DATABASE_NAME], cwd=out)
        self.safe_unlink(out)
        return True

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
        files = [os.path.join("etc", f) for f in os.listdir("etc")
                 if f.endswith(".conf") and not f.startswith(".")]
        files += [os.path.join("etc", "ssh", f)
                  for f in os.listdir(os.path.join("etc", "ssh"))
                  if not f.startswith(".")]
        self.tar(etc_out, files)
        return True

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
