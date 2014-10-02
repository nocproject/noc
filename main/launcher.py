# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-launcher daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import time
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
from noc.lib.log import PrefixLoggerAdapter

logger = logging.getLogger(__name__)


class DaemonData(object):
    """
    Daemon wrapper
    """
    def __init__(self, name, is_superuser, enabled, user, uid, group, gid,
                 instance_id, config_path):
        self.logger = PrefixLoggerAdapter(logger, "%s#%s" % (name, instance_id))
        self.logger.info("Reading config")
        self.instance_id = instance_id
        self.name = name
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

    def __repr__(self):
        return "<DaemonData %s>" % self.name

    def launch(self):
        """
        Launch daemon
        """
        logger.info("Launching")
        try:
            pid = os.fork()
        except OSError, e:
            self.loger.error("Fork failed: %s(%s)", e.strerror, e.errno)
            return
        if pid:
            self.pid = pid
            self.logger.info("Daemon started as PID %d", self.pid)
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
                self.logger.error("OS Error: %s(%s)", e.strerror, e.errno)
                sys.exit(1)

    def kill(self):
        """
        Kill daemon
        """
        if not self.pid:
            self.logger.info("No PID to kill")
        try:
            self.logger.info("Killing")
            os.kill(self.pid, signal.SIGTERM)
        except Exception, why:
            self.logger.error("Unable to kill daemon: %s", why)


class Launcher(Daemon):
    """
    noc-launcher daemon
    """
    daemon_name = "noc-launcher"
    create_piddir = True

    DAEMONS = ["scheduler",
               "web", "sae", "activator",
               "classifier", "collector", "correlator",
               "notifier", "pmwriter", "probe",
               "discovery", "sync"]

    def __init__(self):
        self.next_update_check = 0
        self.next_update_check_interval = 300
        self.is_superuser = os.getuid() == 0  # @todo: rewrite
        self.crashinfo_uid = None
        self.crashinfo_dir = None
        super(Launcher, self).__init__()
        self.daemons = []
        gids = {}
        uids = {}
        for n in self.DAEMONS:
            dn = "noc-%s" % n
            # Check daemon is enabled
            if not self.config.getboolean(dn, "enabled"):
                self.logger.info("%s daemon is disabled", dn)
                continue
            # Check daemon has config (for cloned activators)
            if not os.access("etc/%s.defaults" % dn, os.R_OK):
                self.logger.info("Missed config for %s. Skipping", dn)
                continue
            # Resolve group name
            group_name = self.config.get(dn, "group")
            if group_name:
                if group_name not in gids:
                    try:
                        gid = grp.getgrnam(group_name)[2]
                        gids[group_name] = gid
                    except KeyError:
                        self.logger.error(
                            "%s: Group '%s' is not found. Exiting.",
                            dn, group_name
                        )
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
                        self.logger.error(
                            "%s: User '%s' is not found. Exiting.",
                            dn, user_name
                        )
                        sys.exit(1)
                uid = uids[user_name]
            else:
                uid = None
            # Superuser required to change uid/gid
            if not self.is_superuser and uids:
                self.logger.error("Need to be superuser to change UID")
                sys.exit(1)
            if not self.is_superuser and gids:
                self.logger.error("Need to be superuser to change GID")
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
            # Set crashinfo uid
            if self.is_superuser and dn == "noc-sae":
                self.crashinfo_uid = uid
                self.crashinfo_dir = os.path.dirname(self.config.get("main", "logfile"))

    def load_config(self):
        super(Launcher, self).load_config()
        if self.config.getboolean("update", "enabled"):
            self.update_url = self.config.get("update", "url") or None
            self.next_update_check_interval = self.config.getint("update", "check_interval")
        else:
            self.update_url = None

    def run(self):
        """
        Main loop
        """
        self.logger.info("Running")
        # Check for updates
        if self.update_url:
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
                        d.logger.info(
                            "Terminated with status %d",
                            os.WEXITSTATUS(status)
                        )
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
                        self.logger.info("Permissions for %s are fixed",
                                         path
                        )
                    except:
                        self.logger.error(
                            "Failed to fix permissions for %s",
                            path
                        )
                last_crashinfo_check = t
            # Check for updates
            if self.update_url and t > self.next_update_check:
                self.check_updates()

    def check_updates(self):
        if not self.update_url:
            return
        # Update
        self.logger.info("Checking for updates")
        daemons = set(d.name for d in self.daemons)
        uc = UpdateClient(self.update_url, daemons)
        if uc.request_updates():
            # Updated, restart
            self.logger.info("Updates are applied. Restarting")
            self.stop_all_daemons()
            os.execv(sys.argv[0], sys.argv)
        self.next_update_check = time.time() + self.next_update_check_interval

    def stop_all_daemons(self):
        for d in self.daemons:
            if d.enabled and d.pid:
                try:
                    self.logger.info("Stopping daemon: %s (PID %d)",
                        d.logname, d.pid)
                    os.kill(d.pid, signal.SIGTERM)
                    d.pid = None
                except OSError:
                    pass

    def at_exit(self):
        self.stop_all_daemons()
        super(Launcher, self).at_exit()
