# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Beward
# OS:     BD
# ProdNbr=BD75-1
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python module
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Beward.BD"
    config_tokenizer = "line"
    config_tokenizer_settings = {"line_comment": "#", "rewrite": [(re.compile(r"[\.=\[\]]"), " ")]}
    config_normalizer = "BDNormalizer"
    confdb_defaults = [
        ("hints", "protocols", "ntp", "mode", "client"),
        ("hints", "protocols", "ntp", "version", "3"),
    ]
