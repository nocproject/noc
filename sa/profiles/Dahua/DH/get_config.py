# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Dahua.DH.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Dahua.DH.get_config"
    interface = IGetConfig
    config_sections = [
        "General",
        "Network",
        "RTSP",
        "VideoColor",
        "VideoInOptions",
        "Encode",
        "VideoStandard",
        "Ptz",
        "VideoInDayNight",
        "NTP",
        "VideoWidget",
        "ChannelTitle",
    ]  # "VideoOut"

    def execute(self, **kwargs):
        res = self.http.get(
            "/cgi-bin/configManager.cgi?action=getConfig&%s"
            % "&".join(["%s=%s" % ("name", c) for c in self.config_sections])
        )
        users_info = self.http.get("/cgi-bin/userManager.cgi?action=getUserInfoAll")

        return res + users_info
