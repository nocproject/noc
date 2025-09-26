# ---------------------------------------------------------------------
# Config check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.error import NOCError
from noc.services.discovery.jobs.base import DiscoveryCheck


class ConfigCheck(DiscoveryCheck):
    """
    Version discovery
    """

    name = "config"
    required_script = "get_config"
    fatal_errors = {}

    def handler(self):
        # Get config
        self.logger.info("Checking config")
        config = self.get_config()
        if not config:
            self.logger.error("Cannot get config")
            return
        # Save config
        changed = self.object.save_config(config, validate=False)
        self.set_artefact("config_changed", changed)
        self.set_artefact("config_acquired", True)
        # Create ConfDB artefact
        if not self.object.has_confdb_support:
            self.logger.error("ConfDB is not supported. Skipping all following ConfDB checks")
            return
        if not self.job.is_confdb_required():
            self.logger.info("ConfDB is not required. Skipping")
            return
        self.logger.info("Building ConfDB")
        confdb = self.object.get_confdb(config)
        self.set_artefact("confdb", confdb)

    def get_config(self):
        p = self.object.get_config_policy()
        if p == "s":  # Script
            return self.get_config_script()
        if p == "S":  # Script, Download
            return self.get_config_script() or self.get_config_download()
        if p == "D":  # Download, Script
            return self.get_config_download() or self.get_config_script()
        if p == "d":  # Download
            return self.get_config_download()
        self.logger.error("Invalid config policy: %s", p)
        return None

    def get_config_script(self):
        if self.required_script not in self.object.scripts:
            self.logger.info(
                "%s script is not supported. Cannot request config from device",
                self.required_script,
            )
            return None
        self.logger.info("Requesting config from device")
        try:
            return self.object.scripts.get_config(policy=self.object.get_config_fetch_policy())
        except NOCError as e:
            self.logger.error("Failed to request config: %s", e)
            if hasattr(e, "remote_code"):
                self.set_problem(
                    alarm_class=self.error_map.get(e.remote_code),
                    message=f"RPC Error: {e}",
                    diagnostic="CLI" if e.remote_code in self.error_map else None,
                )

    def get_config_download(self):
        self.logger.info("Downloading config from external storage")
        # Check storage is set
        storage = self.object.object_profile.config_download_storage
        if not storage:
            self.logger.error("Failed to download. External storage is not set")
            return None
        # Check path template
        tpl = self.object.object_profile.config_download_template
        if not tpl:
            self.logger.error("Failed to download. Path template is not set")
            return None
        # Render path
        path = tpl.render_subject(object=self.object).strip()
        if not path:
            self.logger.error("Failed to download. Empty path")
            return None
        # Download
        self.logger.info("Downloading from %s:%s", storage.name, path)
        try:
            with storage.open_fs() as fs:
                with fs.open(path) as f:
                    return f.read()
        except storage.Error as e:
            self.logger.info("Failed to download: %s", e)
            return None

    def has_required_script(self):
        return super().has_required_script() or self.object.get_config_policy() != "s"
