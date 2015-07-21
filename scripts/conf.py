#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Distributed config manipulation
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import sys
from optparse import OptionParser, make_option, OptionError, OptParseError
import ConfigParser
import os
import glob
import tempfile
import subprocess
## Third-party modules
import consul.base
import consul
## NOC modules
from noc.lib.service.base import Service
from noc.sa.interfaces.base import DictParameter


# Read node config
env = None
dc = None
node = None
if os.path.exists("etc/config/env/supervisord.conf"):
    config = ConfigParser.SafeConfigParser()
    config.read("etc/config/env/supervisord.conf")
    if config.has_option("supervisord", "NOC_ENV"):
        env = config.get("supervisord", "NOC_ENV")
    if config.has_option("supervisord", "NOC_DC"):
        dc = config.get("supervisord", "NOC_DC")
    if config.has_option("supervisord", "NOC_NODE"):
        node = config.get("supervisord", "NOC_NODE")
# Read services config
services = {}
for p in glob.glob("services/*/service.py"):
    sn = p.split(os.sep)[1]
    services[sn] = None

option_list = [
    make_option(
        "-f", "--format",
        action="store", dest="format",
        choices=["info", "json", "yaml"],
        default="yaml",
        help="Output format [Choices: info, json, yaml. Default %default]"
    ),
    make_option(
        "--env",
        action="store", dest="env",
        default=env,
        help="Environment [Default: %default]"
    ),
    make_option(
        "--datacenter",
        action="store", dest="dc",
        default=dc,
        help="Datacenter [Default: %default]"
    ),
    make_option(
        "--node",
        action="store", dest="node",
        default=node,
        help="Node [Default: %default]"
    ),
    make_option(
        "--global",
        action="store_true", dest="glob",
        default=False,
        help="Global configuration"
    ),
    make_option(
        "-s", "--service",
        action="store", dest="service",
        choices=list(services),
        help="Service [Choices: %s]" % ", ".join(sorted(services))
    ),
    make_option(
        "--show",
        action="store_const", dest="action", const="show",
        default="show",
        help="Show config"
    ),
    make_option(
        "--edit",
        action="store_const", dest="action", const="edit",
        help="Edit config"
    )

]

usage = "usage: %prog [options] arg1 arg2 ..."


def die(msg):
    sys.stderr.write(str(msg) + "\n")
    sys.stderr.flush()
    sys.exit(1)


def conf_path(conf):
    """
    Return config path
    """
    if conf.glob:
        return "noc/%s/config/global/%s/" % (conf.env, conf.service)
    else:
        return "noc/%s/config/dc/%s/node/%s/%s/" % (
            conf.env, conf.dc, conf.node, conf.service
        )


def get_consul(conf):
    return consul.Consul(
        dc=conf.dc or None
    )


def get_data(conf):
    c = get_consul(conf)
    path = conf_path(conf)
    try:
        index, data = c.kv.get(path, recurse=True)
    except consul.base.Timeout:
        die("Connection timeout")
    if data:
        d = dict(
            (str(x["Key"].rsplit("/", 1)[-1]), x["Value"])
            for x in data)
    else:
        d = {}
    return {
        conf.service: d
    }


def get_editor():
    """
    Get editor to use
    """
    editor = "vi"
    return os.environ.get("VISUAL") or os.environ.get("EDITOR", editor)


def action_show(conf, args):
    """
    Show configuration node
    """
    d = get_data(conf)
    print format(conf, d)


def action_edit(conf, args):
    """
    Edit configuration node
    """
    # Find interface
    m = __import__("noc.services.%s.service" % conf.service, {}, {}, "*")
    interface = None
    for a in dir(m):
        o = getattr(m, a)
        if isinstance(o, type) and issubclass(o, Service):
            interface = DictParameter(attrs=o.config_interface,
                                      truncate=True)
    if not interface:
        die("Service cannot be configured")
    #
    d = get_data(conf)
    # Save text to file
    rd = format(conf, d)
    fd, name = tempfile.mkstemp(
        prefix="noc-conf-",
        suffix=".yaml", text=True
    )
    try:
        f = os.fdopen(fd, "w")
        f.write(rd)
        f.close()
        editor = get_editor()
        rc = subprocess.call(
            "\"%s\" \"%s\"" % (editor, name),
            shell=True, close_fds=True
        )
        if rc:
            die("Failed to edit")
        with open(name) as f:
            nd = f.read()
        if nd == rd:
            die("Not changed, aborting")
    finally:
        os.unlink(name)
    # Apply config. Calculate differencies
    data = decode(conf, nd)
    # Verify
    try:
        data[conf.service] = interface.clean(data[conf.service])
    except ValueError, why:
        die("ERROR: %s" % why)
    print data


def format(conf, data):
    if conf.format == "json":
        return format_json(conf.service, data)
    elif conf.format == "yaml":
        return format_yaml(conf.service, data)


def decode(conf, data):
    """
    Decode data according to format
    """
    if conf.format == "yaml":
        return decode_yaml(data)


def format_json(name, data):
    """
    JSON format
    """
    import json
    return json.dumps(data)


def format_yaml(name, data):
    """
    YAML output
    """
    import yaml
    return yaml.dump(data, default_flow_style=False)


def decode_yaml(data):
    import yaml
    return yaml.load(data)

def main():
    parser = OptionParser(
        usage=usage,
        option_list=option_list
    )
    try:
        conf, args = parser.parse_args()
    except OptionError, why:
        return die(why)
    except OptParseError, why:
        return die(why)
    if conf.action == "show":
        action_show(conf, args)
    elif conf.action == "edit":
        action_edit(conf, args)

if __name__ == "__main__":
    main()
