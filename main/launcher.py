# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-launcher daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import time
import subprocess
import sys
import os
import logging
import ConfigParser
import pwd
import grp
import signal
import stat
## NOC modules
from noc.lib.daemon import Daemon
from noc.lib.debug import DEBUG_CTX_CRASH_PREFIX
from noc.lib.updateclient import UpdateClient

## Heartbeat check interval
HEARTBEAT_TIMEOUT = 10
UPDATE_INTERVAL = 300


class DaemonData(object):
    """
    Daemon wrapper
    """
    def __init__(self, name, is_superuser, enabled, user, uid, group, gid,
                 instance_id, config_path):
        logging.debug("Reading config for %s[#%s]: %s" % (
            name, instance_id, config_path))
        self.instance_id = instance_id
        self.name = name
        self.logname = "%s[#%s]" % (self.name, self.instance_id)
        self.config_path = config_path
        self.config = ConfigParser.SafeConfigParser()
        self.config.read("etc/%s.defaults" % name)
        self.config.read(config_path)
        self.enabled = enabled
        self.pid = None
        self.pidfile = self.config.get("main", "pidfile")\
            .replace("{{instance}}", self.instance_id)
        self.is_superuser = is_superuser
        self.user = user
        self.uid = uid
        self.group = group
        self.gid = gid
        self.enable_heartbeat = self.config.getboolean("main", "heartbeat")
        self.next_heartbeat_check = 0
        # Set up update paths
        self.update_name = None
        if (self.config.has_section("update") and
                self.config.has_option("update", "enabled") and
                self.config.getboolean("update", "enabled")):
            self.update_name = self.config.get("update", "name")

    def __repr__(self):
        return "<DaemonData %s>" % self.name

    def launch(self):
        """
        Launch daemon
        """
        logging.info("Launching %s" % self.logname)
        try:
            pid = os.fork()
        except OSError, e:
            logging.error("%s: Fork failed: %s(%s)" % (self.logname,
                                                       e.strerror, e.errno))
            return
        if pid:
            self.pid = pid
            logging.info("Daemon %s started as PID %d" % (self.logname,
                                                          self.pid))
            self.next_heartbeat_check = time.time() + HEARTBEAT_TIMEOUT
        else:
            # Run child
            try:
                if self.group:
                    os.setgid(self.gid)
                    os.setegid(self.gid)
                if self.user:
                    os.setuid(self.uid)
                    os.seteuid(self.uid)
                    # Set up EGG Cache to prevent permissions problem in python 2.6
                    os.environ["PYTHON_EGG_CACHE"] = "/tmp/.egg-cache%d" % self.uid
                    # Adjust HOME and USER environment variables
                    os.environ["USER"] = self.user
                    os.environ["HOME"] = pwd.getpwuid(self.uid).pw_dir
                os.execv(sys.executable,
                         [sys.executable, "./scripts/%s.py" % self.name,
                          "launch", "-c", self.config_path,
                          "-i", self.instance_id])
            except OSError, e:
                logging.error("%s: OS Error: %s(%s)" % (self.logname,
                                                        e.strerror, e.errno))
                sys.exit(1)

    def kill(self):
        """
        Kill daemon
        """
        if not self.pid:
            logging.info("%s: No PID to kill" % self.logname)
        try:
            logging.info("%s: killing" % self.logname)
            os.kill(self.pid, signal.SIGTERM)
        except Exception:
            logging.error("%s: Unable to kill daemon" % self.logname)

    def check_heartbeat(self):
        """
        Check daemons heartbeat
        """
        if not self.enabled or not self.pid or not self.enable_heartbeat:
            return
        t = time.time()
        if t < self.next_heartbeat_check:
            return
        logging.debug("Checking heartbeat from %s" % self.logname)
        self.next_heartbeat_check = t + HEARTBEAT_TIMEOUT
        try:
            mt = os.stat(self.pidfile)[stat.ST_MTIME]
        except OSError:
            logging.error("Unable to stat pidfile: %s" % self.pidfile)
            return
        if t - mt >= HEARTBEAT_TIMEOUT:
            logging.info("%s: Heartbeat lost. Restarting" % self.logname)
            self.kill()


class Launcher(Daemon):
    """
    noc-launcher daemon
    """
    daemon_name = "noc-launcher"
    create_piddir = True

    DAEMONS = ["stomp", "scheduler", "wf",
               "web", "sae", "activator",
               "classifier", "collector", "correlator",
               "notifier", "pmwriter", "probe",
               "discovery", "sync"]

    def __init__(self):
        super(Launcher, self).__init__()
        self.daemons = []
        gids = {}
        uids = {}
        self.update_url = self.config.get("update", "url")
        self.update_names = set()
        if (self.config.getboolean("update", "enabled") and
                self.config.get("update", "name")):
            self.update_names.add(self.config.get("update", "name"))
        self.next_update_check = 0
        self.is_superuser = os.getuid() == 0  # @todo: rewrite
        self.crashinfo_uid = None
        self.crashinfo_dir = None
        for n in self.DAEMONS:
            dn = "noc-%s" % n
            # Check daemon is enabled
            if not self.config.getboolean(dn, "enabled"):
                logging.info("%s daemon is disabled" % dn)
                continue
            # Check daemon has config (for cloned activators)
            if not os.access("etc/%s.defaults" % dn, os.R_OK):
                logging.info("Missed config for %s. Skipping" % dn)
                continue
            # Resolve group name
            group_name = self.config.get(dn, "group")
            if group_name:
                if group_name not in gids:
                    try:
                        gid = grp.getgrnam(group_name)[2]
                        gids[group_name] = gid
                    except KeyError:
                        logging.error("%s: Group '%s' is not found. Exiting." % (dn, group_name))
                        sys.exit(1)
                gid = gids[group_name]
            else:
                gid = None
            # Resolve user name
            user_name = self.config.get(dn, "user")
            if user_name:
                if user_name not in uids:
                    try:
                        uid = pwd.getpwnam(user_name)[2]
                        uids[user_name] = uid
                    except KeyError:
                        logging.error("%s: User '%s' is not found. Exiting." % (dn, user_name))
                        sys.exit(1)
                uid = uids[user_name]
            else:
                uid = None
            # Superuser required to change uid/gid
            if not self.is_superuser and uids:
                logging.error("Need to be superuser to change UID")
                sys.exit(1)
            if not self.is_superuser and gids:
                logging.error("Need to be superuser to change GID")
                sys.exit(1)
            # Check for configs and daemon instances
            opts = self.config.options(dn)
            if "config" in opts and self.config.get(dn, "config"):
                configs = [("0", self.config.get(dn, "config"))]
            else:
                configs = [(c[7:], self.config.get(dn, c))
                           for c in opts if c.startswith("config.")]
            # Initialize daemon data
            for instance_id, config in configs:
                dd = DaemonData(
                    dn,
                    is_superuser=self.is_superuser,
                    enabled=True,
                    user=user_name,
                    uid=uid,
                    group=group_name,
                    gid=gid,
                    instance_id=instance_id,
                    config_path=config
                )
                self.daemons += [dd]
                if dd.update_name:
                    self.update_names.add(dd.update_name)
            # Set crashinfo uid
            if self.is_superuser and dn == "noc-sae":
                self.crashinfo_uid = uid
                self.crashinfo_dir = os.path.dirname(self.config.get("main", "logfile"))

    def run(self):
        """
        Main loop
        """
        # Check for updates
        self.check_updates()
        # Main loop
        last_crashinfo_check = time.time()
        while True:
            for d in self.daemons:
                if not d.enabled:  # Skip disabled daemons
                    continue
                if d.pid is None:  # Launch required daemons
                    d.launch()
                else:  # Check daemon status
                    try:
                        pid, status = os.waitpid(d.pid, os.WNOHANG)
                    except OSError:
                        pid = 0
                        status = 0
                    if pid == d.pid:
                        logging.info("%s daemon is terminated with status %d" % (d.logname, os.WEXITSTATUS(status)))
                        d.pid = None
            time.sleep(1)
            t = time.time()
            if self.crashinfo_uid is not None and t - last_crashinfo_check > 10:
                # Fix crashinfo's permissions
                for fn in [fn for fn in os.listdir(self.crashinfo_dir) if fn.startswith(DEBUG_CTX_CRASH_PREFIX)]:
                    path = os.path.join(self.crashinfo_dir, fn)
                    try:
                        if os.stat(path)[stat.ST_UID] == self.crashinfo_uid:
                            continue  # No need to fix
                    except OSError:
                        continue  # stat() failed
                    try:
                        os.chown(path, self.crashinfo_uid, -1)
                        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
                        logging.info("Permissions for %s are fixed" % path)
                    except:
                        logging.error("Failed to fix permissions for %s" % path)
                last_crashinfo_check = t
            # Check for updates
            if self.update_names and t > self.next_update_check:
                self.check_updates()
            # Check heartbeats
            [d for d in self.daemons if d.check_heartbeat()]

    def check_updates(self):
        if not self.update_names:
            return
        update_names = sorted(self.update_names)
        # Update
        logging.info("Checking for updates: %s" % ", ".join(update_names))
        uc = UpdateClient(self.update_url, update_names)
        if uc.request_update():
            # Updated, restart
            logging.info("Updates are applied. Restarting")
            self.stop_all_daemons()
            os.execv(sys.argv[0], sys.argv)
        self.next_update_check = time.time() + UPDATE_INTERVAL

    def stop_all_daemons(self):
        for d in self.daemons:
            if d.enabled and d.pid:
                try:
                    logging.info("Stopping daemon: %s (PID %d)" % (
                        d.logname, d.pid))
                    os.kill(d.pid, signal.SIGTERM)
                    d.pid = None
                except OSError:
                    pass

    def at_exit(self):
        self.stop_all_daemons()
        super(Launcher, self).at_exit()
