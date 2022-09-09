# ---------------------------------------------------------------------
# Vendor: Hikvision
# OS:     DSKV8
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Hikvision.DSKV8"

    config_tokenizer = "indent"
    config_tokenizer_settings = {"line_comment": "#"}
    config_normalizer = "HikvisionNormalizer"
    confdb_defaults = [("hints", "protocols", "ntp", "mode", "server")]
