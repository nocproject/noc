# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NSD zone file backend
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import os
import re
import subprocess
## NOC modules
from noc.main.sync.channel import Channel
from noc.dns.utils.zonefile import ZoneFile


class NSDFileChannel(Channel):
    """
    Config example:

    [dns/zone/ch1]
    type = nsd/file
    enabled = true
    root = <zone files directory>
    inc_root = <relative path to zone file>
    on_reload = nsdc rebuild
    on_reload_zone =
    """
    def __init__(self, daemon, channel, name, config):
        super(NSDFileChannel, self).__init__(
            daemon, channel, name, config)
        self.zones = config["root"]
        self.inc_root = config.get("inc_root")
        if not os.path.isdir(self.zones):
            self.die("Cannot open directory %s" % self.zones)
        self.manifest = os.path.join(self.zones, ".manifest")
        self.include = os.path.join(self.zones, "noc_zones.conf")
        self.cmd_reload = config.get("on_reload")
        if not self.cmd_reload:
            self.cmd_reload = "rndc reload"
        self.cmd_reload_zone = config.get("on_reload_zone")
        if not self.cmd_reload_zone:
            self.cmd_reload_zone = "rndc reload {{ zone }}"

    def get_zone_path(self, zone):
        """
        Get absolute zone file path
        :param zone:
        :return:
        """
        return os.path.join(self.zones, zone)

    def get_zone_inc_path(self, zone):
        """
        Get relative zone file path for include file
        :param zone:
        :return:
        """
        if self.inc_root:
            return os.path.join(self.inc_root, zone)
        else:
            return self.get_zone_path(zone)

    def get_manifest(self):
        """
        Parse manifest file
        :return: dict of name -> serial
        """
        if not os.path.isfile(self.manifest):
            return {}
        d = {}
        with open(self.manifest) as f:
            for l in f:
                l = l.strip()
                if l:
                    z, s = l.split(" ", 1)
                    d[z] = int(s)
        return d

    def write_manifest(self, mf):
        """
        Save manifest to file and update include file
        :param mf:
        :return:
        """
        fv = "\n".join("%s %d" % (z, mf[z]) for z in sorted(mf))
        with open(self.manifest, "w") as f:
            f.write(fv)

    def write_include(self, mf):
        """
        Write include file
        :param mf:
        :return:
        """
        # Update include file
        self.info("Updating %s" % self.include)
        ifile = [
            "#",
            "# NOC provisioned zones",
            "# WARNING: This is auto-generated file",
            "# Do not edit manually",
            "#",
            ""
        ]
        for z in sorted(mf):
            ifile += [
                "# %s" % z,
                "zone:",
                "    name: %s" % z,
                "    zonefile: %s" % self.get_zone_inc_path(z),
                ""
            ]
        ifile = "\n".join(ifile)
        with open(self.include, "w") as f:
            f.write(ifile)

    def update_manifest(self, mf, zone, serial):
        if mf.get(zone) == serial:
            return  # No need to update
        is_new = zone not in mf
        mf[zone] = serial
        self.write_manifest(mf)
        if is_new:
            self.write_include(mf)
            self.reload()
        else:
            self.reload_zone(zone)

    def on_list(self, items):
        """
        :param items: Dict of name -> version
        :return:
        """
        mf = self.get_manifest()
        missed = [z for z in items
                  if (z not in mf or items[z] != mf[z])]
        # Remove hanging domains
        removed = set(mf) - set(items)
        if removed:
            # Update manifest
            for r in removed:
                del mf[r]
            self.write_manifest(mf)
            # Update include file
            self.write_include(mf)
            # Remove hanging zones
            for r in removed:
                self.info("Removing hanging zone %s" % r)
                fp = self.get_zone_path(r)
                if os.path.isfile(fp):
                    os.unlink(fp)
            # Refresh nameserver config
            self.reload()
        # Request missed domains
        if missed:
            self.verify(missed)

    def on_verify(self, object, data):
        """
        :param object: zone name
        :param data: dict of
            *serial* - Zone serial
            *records* - list of (name, type, content, ttl, priority)
        :return:
        """
        serial = int(data["serial"])
        mf = self.get_manifest()
        if mf.get(object) == serial:
            return  # Actual
        zf = ZoneFile(object, data["records"]).get_text()
        path = self.get_zone_path(object)
        self.info("Updating %s (%d)" % (object, serial))
        with open(path, "w") as f:
            f.write(zf)
        self.update_manifest(mf, object, serial)

    def reload(self):
        """
        Reload named config
        :return:
        """
        cmd = self.cmd_reload
        self.info("Running `%s`" % cmd)
        r = subprocess.call(cmd, shell=True)
        if r:
            self.info("Failed to run `%s`: exit code %d" % (cmd, r))
        else:
            self.info("OK")

    rx_tpl = re.compile("{{\s*(?P<var>\S+)\s*}}")

    def reload_zone(self, zone):
        """
        Reload named zone
        :param zone:
        :return:
        """
        ctx = {"zone": zone}
        cmd = self.rx_tpl.sub(lambda m: ctx[m.group("var")],
            self.cmd_reload_zone)
        self.info("Running `%s`" % cmd)
        r = subprocess.call(cmd, shell=True)
        if r:
            self.info("Failed to run `%s`: exit code %d" % (cmd, r))
        else:
            self.info("OK")
