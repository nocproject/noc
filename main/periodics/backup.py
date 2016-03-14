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
from noc.core.config.base import config as cfg


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
        backup_dir = config.get("path", "backup_dir")
        keep_days = config.getint("backup", "keep_days")
        keep_weeks = config.getint("backup", "keep_weeks")
        keep_day_of_week = config.getint("backup", "keep_day_of_week")
        keep_months = config.getint("backup", "keep_months")
        keep_day_of_month = config.getint("backup", "keep_day_of_month")

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
        except OSError, why:
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
            except OSError, why:
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
        pgpass = ["*", "*", "*", "*", ""]  # host, port, database, user, password
        out = "noc-db-%04d-%02d-%02d-%02d-%02d.dump" % (now.year, now.month,
                                                        now.day, now.hour,
                                                        now.minute)
        out = os.path.join(config.get("path", "backup_dir"), out)
        # Build pg_dump command and options
        cmd = [config.get("path", "pg_dump"), "-Fc"]
        cmd += ["-f", out]
        if cfg.pg_user:
            cmd += ["-U", cfg.pg_user]
            pgpass[3] = cfg.pg_user
        if cfg.pg_password:
            pgpass[4] = cfg.pg_password
        cmd += ["-h", cfg.pg_connection_args["host"]]
        pgpass[0] = cfg.pg_connection_args["host"]
        if cfg.pg_connection_args["port"]:
            cmd += ["-p", str(cfg.pg_connection_args["port"])]
            pgpass[1] = cfg.pg_connection_args["port"]
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
               "-d", cfg.mongo_db,
               "-o", out,
               "-h", cfg.mongo_connection_args["url"]]
        if cfg.mongo_user:
            cmd += ["-u", cfg.mongo_user]
        if cfg.mongo_password:
            cmd += ["-p", cfg.mongo_password]
        self.info("Dumping MongoDB database into %s" % out)
        retcode = self.subprocess_call(cmd)
        if retcode:
            self.error("dump failed. Removing broken dump %s" % out)
            self.safe_unlink(out)
            return False
        self.info("Archiving dump")
        r = self.tar(out + ".tar.gz", [cfg.mongo_db], cwd=out)
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
        except OSError, why:
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
