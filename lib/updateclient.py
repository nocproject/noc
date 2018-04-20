# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Remote daemon's update client
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import urllib2
import logging
import subprocess
import json
import socket
## Third-party modules
from mercurial import ui, localrepo, commands

logger = logging.getLogger(__name__)


class UpdateClient(object):
    PIP_FIND_LINKS = "https://bitbucket.org/nocproject/noc/downloads"

    def __init__(self, url, daemons):
        if not url.endswith("/"):
            url += "/"
        self.url = url + "main/update/"
        self.repo = localrepo.localrepository(ui.ui(), path=".")
        self.tip = "".join("%02x" % ord(c) for c in self.repo.changelog.tip())
        self.branch = self.repo.dirstate.branch()
        self.daemons = daemons

    def request_updates(self):
        # Get required revision
        logger.info("Requesting updates from %s", self.url)
        try:
            f = urllib2.urlopen(self.url, timeout=30)
            data = json.loads(f.read())[0]
            f.close()
        except urllib2.URLError, why:
            logger.error("Failed to get updates: %s", why)
            return False
        except socket.error, why:
            logger.error("Socket error: %s", why)
            return False
        # Compare
        if self.branch != data["branch"]:
            logger.info("Switching to branch %s", data["branch"])
            logger.debug("hg update -r %s", data["branch"])
            r = commands.update(ui.ui(), self.repo, rev=data["branch"])
            if r:
                logger.error("Failed to switch branch")
                return False
        if self.tip != data["tip"]:
            logger.info("Upgrading from %s to %s",
                        self.tip[:12], data["tip"][:12])
            logger.debug("hg pull -b %s -r %s -u %s",
                         data["branch"], data["tip"], data["repo"])
            r = commands.pull(ui.ui(), self.repo, source=data["repo"],
                              update=True,
                              branch=[data["branch"]], rev=[data["tip"]])
            if r:
                logger.error("Failed to pull updates")
                return False
            return self.update_packages()
        logger.debug("Nothing to update")
        return False

    def update_packages(self):
        logger.info("Upgrading packages")
        requirements = ["etc/requirements/common.txt"]
        for n in self.daemons:
            if n.startswith("noc-"):
                n = n[4:]
            rn = "etc/requirements/%s.txt" % n
            if os.path.isfile(rn):
                requirements += [rn]
        r = " ".join("-r %s" % x for x in requirements)
        cmd = "./bin/pip install %s --find-links %s --allow-all-external --upgrade" % (
            r, self.PIP_FIND_LINKS)
        logger.debug("Running: %s", cmd)
        r = subprocess.call(cmd, shell=True)
        if r:
            logger.error("Failed to update packages")
            return False
        else:
            logger.debug("Packages are up-to-date")
            return True
