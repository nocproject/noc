# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
## Third-party modules
from south.db import db


class Migration:
    RENAME_COLUMNS = [
        # Box
        ("enable_box_discovery_version", "enable_version_inventory"),
        ("enable_box_discovery_caps", "enable_caps_discovery"),
        ("enable_box_discovery_interface", "enable_interface_discovery"),
        ("enable_box_discovery_id", "enable_id_discovery"),
        ("enable_box_discovery_config", "enable_config_discovery"),
        ("enable_box_discovery_asset", "enable_asset_discovery"),
        ("enable_box_discovery_prefix", "enable_prefix_discovery"),
        ("enable_box_discovery_vlan", "enable_vlan_discovery"),
        ("enable_box_discovery_bfd", "enable_bfd_discovery"),
        ("enable_box_discovery_cdp", "enable_cdp_discovery"),
        ("enable_box_discovery_fdp", "enable_fdp_discovery"),
        ("enable_box_discovery_lldp", "enable_lldp_discovery"),
        ("enable_box_discovery_oam", "enable_oam_discovery"),
        ("enable_box_discovery_rep", "enable_rep_discovery"),
        ("enable_box_discovery_stp", "enable_stp_discovery"),
        ("enable_box_discovery_udld", "enable_udld_discovery"),
        # Periodic
        ("enable_periodic_discovery_uptime", "enable_uptime_discovery"),
        ("enable_periodic_discovery_interface_status",
         "enable_interface_status_discovery"),
        ("enable_periodic_discovery_mac", "enable_mac_discovery"),
        ("enable_periodic_discovery_ip", "enable_ip_discovery"),
    ]

    DROP_COLUMNS = [
        "config_discovery_min_interval",
        "config_discovery_max_interval",
        "version_inventory_min_interval",
        "version_inventory_max_interval",
        "caps_discovery_min_interval",
        "caps_discovery_max_interval",
        "uptime_discovery_min_interval",
        "uptime_discovery_max_interval",
        "interface_discovery_min_interval",
        "interface_discovery_max_interval",
        "prefix_discovery_min_interval",
        "prefix_discovery_max_interval",
        "interface_status_discovery_min_interval",
        "interface_status_discovery_max_interval",
        "ip_discovery_min_interval",
        "ip_discovery_max_interval",
        "vlan_discovery_min_interval",
        "vlan_discovery_max_interval",
        "mac_discovery_min_interval",
        "mac_discovery_max_interval",
        "id_discovery_min_interval",
        "id_discovery_max_interval",
        "lldp_discovery_min_interval",
        "lldp_discovery_max_interval",
        "cdp_discovery_min_interval",
        "cdp_discovery_max_interval",
        "fdp_discovery_min_interval",
        "fdp_discovery_max_interval",
        "bfd_discovery_min_interval",
        "bfd_discovery_max_interval",
        "rep_discovery_min_interval",
        "rep_discovery_max_interval",
        "stp_discovery_min_interval",
        "stp_discovery_max_interval",
        "udld_discovery_min_interval",
        "udld_discovery_max_interval",
        "oam_discovery_min_interval",
        "oam_discovery_max_interval",
        "asset_discovery_min_interval",
        "asset_discovery_max_interval",
    ]

    def forwards(self):
        # Rename columns
        for o, n in self.RENAME_COLUMNS:
            db.rename_column("sa_managedobjectprofile", n, o)
        # Create new columns
        db.add_column(
            "sa_managedobjectprofile",
            "enable_box_discovery",
            models.BooleanField(default=False)
        )
        db.add_column(
            "sa_managedobjectprofile",
            "box_discovery_interval",
            models.IntegerField(default=86400)
        )
        db.add_column(
            "sa_managedobjectprofile",
            "box_discovery_failed_interval",
            models.IntegerField(default=10800)
        )
        db.add_column(
            "sa_managedobjectprofile",
            "box_discovery_on_system_start",
            models.BooleanField(default=False)
        )
        db.add_column(
            "sa_managedobjectprofile",
            "box_discovery_system_start_delay",
            models.IntegerField(default=300)
        )
        db.add_column(
            "sa_managedobjectprofile",
            "box_discovery_on_config_changed",
            models.BooleanField(default=False)
        )
        db.add_column(
            "sa_managedobjectprofile",
            "box_discovery_config_changed_delay",
            models.IntegerField(default=300)
        )
        db.add_column(
            "sa_managedobjectprofile",
            "enable_periodic_discovery",
            models.BooleanField(default=False)
        )
        db.add_column(
            "sa_managedobjectprofile",
            "periodic_discovery_interval",
            models.IntegerField(default=300)
        )
        # Drop deprecated columns
        for n in self.DROP_COLUMNS:
            db.drop_column("sa_managedobjectprofile", n)

    def backwards(self):
        pass
