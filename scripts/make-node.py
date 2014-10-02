#!/usr/bin/env python
##----------------------------------------------------------------------
## Make new NOC node
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import optparse
import sys
import os
import urllib2
import subprocess
import json
import ConfigParser

usage = "usage: %prog [options] <NOC URL>"

URL = ""
PIP_FIND_LINKS = "http://cdn.nocproject.org/pkg/simple/"

def die(msg):
    print msg
    sys.exit(2)


def check_python_version():
    """
    Check python is 2.6 or 2.7
    """
    vi = sys.version_info
    if vi[0] == 2 and vi[1] in (6, 7):
        return
    die("Invalid python version: %s. Python 2.6 or 2.7 required" % sys.version.split()[0])


def check_virtualenv():
    r = subprocess.call("virtualenv --version > /dev/null", shell=True)
    if r:
        die("virtualenv is not found")


def check_hg():
    r = subprocess.call("hg --version > /dev/null", shell=True)
    if r:
        die("mercurial is not found")


def get_info(url):
    try:
        f = urllib2.urlopen(url)
        data = json.loads(f.read())[0]
        f.close()
        return data
    except urllib2.URLError, why:
        die("Failed to get updates: %s" % why)


def create_target(path):
    p = os.path.abspath(os.path.join(path, ".."))
    if not os.path.isdir(p):
        try:
            os.makedirs(p)
        except OSError, why:
            die("Cannot create directory '%s': %s" % (p, why))
    os.chdir(p)
    if os.path.exists("noc"):
        die("Directory %s is already exists" % path)


def clone(repo, branch, tip):
    r = subprocess.call("hg clone -b %s -r %s %s noc" % (branch, tip, repo), shell=True)
    if r:
        die("Cannot clone repo %s" % repo)
    os.chdir("noc")


def make_virtualenv():
    r = subprocess.call("virtualenv --no-site-packages .", shell=True)
    if r:
        die("Cannot init virtualenv")


def install_packages():
    r = subprocess.call(
        "./bin/pip install -r etc/requirements/common.txt --find-links %s --allow-all-external --upgrade" % PIP_FIND_LINKS,
        shell=True
    )
    if r:
        die("Cannot install packages")


def create_configs(url):
    config = ConfigParser.SafeConfigParser()
    config.read("etc/noc-launcher.defaults")
    # Disable all daemons
    for s in config.sections():
        if s.startswith("noc-"):
            config.set(s, "enabled", "false")
    # Setup auto-updates
    config.set("update", "url", url)
    config.set("update", "enabled", "true")
    #
    with open("etc/noc-launcher.conf", "w") as f:
        config.write(f)


def install_pth():
    r = subprocess.call("./scripts/install-pth.py")
    if r:
        die("Cannot install noc.pth")


def install(url, target):
    # Normalize URL
    if not url.endswith("/"):
        url += "/"
    # Normalize target
    target = os.path.abspath(target)
    if not target.split(os.path.sep)[-1] == "noc":
        target = os.path.join(target, "noc")
    #
    update_url = url + "main/update/"
    check_python_version()
    check_virtualenv()
    check_hg()
    create_target(target)
    i = get_info(update_url)
    clone(i["repo"], i["branch"], i["tip"])
    make_virtualenv()
    install_packages()
    install_pth()
    create_configs(url)
    # @todo: print info

if __name__ == "__main__":
    parser = optparse.OptionParser(usage=usage)
    parser.add_option(
        "-v", "--verbose", action="store_true", dest="verbose",
        help="Verbose output"
    )
    parser.add_option(
        "-t", "--target", action="store", dest="target",
        default=os.getcwd(),
        help="Target directory"
    )
    options, args = parser.parse_args()
    url = args[0] if args else URL
    if not url:
        parser.print_help()
        sys.exit(1)
    install(url=url, target=options.target)
