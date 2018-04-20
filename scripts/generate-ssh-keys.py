#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Generate SSH keys according to config
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import ConfigParser
## NOC modules
from noc.sa.script.ssh.keys import generate_pair


def get_activator_configs():
    """
    Read noc-launcher config and retrieve all activator instances configs
    :return:
    """
    config = ConfigParser.SafeConfigParser()
    config.read("etc/noc-launcher.defaults")
    config.read("etc/noc-launcher.conf")
    return [config.get("noc-activator", c) for c in
            config.options("noc-activator") if
            c.startswith("config")]


def get_ssh_key_path(path):
    """
    Returns ssh key path
    :param path:
    :return:
    """
    d_path = "etc/noc-activator.defaults"
    config = ConfigParser.SafeConfigParser()
    config.read(d_path)
    config.read(path)
    return config.get("ssh", "key")


def check_key(path):
    """
    Create ssh keys when necessary
    :param path:
    :return:
    """
    pub_path = path + ".pub"
    if not os.path.exists(path) or not os.path.exists(pub_path):
        print "Generating RSA keys: (%s, %s)" % (path, pub_path)
        generate_pair(path)


def main():
    paths = set([get_ssh_key_path(c) for c in
                 get_activator_configs()])
    for path in paths:
        check_key(path)


if __name__ == "__main__":
    main()
