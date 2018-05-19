# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Access schemes constants
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

TELNET = 1
SSH = 2
HTTP = 3
HTTPS = 4
BEEF = 5

SCHEME_CHOICES = [
    (TELNET, "telnet"),
    (SSH, "ssh"),
    (HTTP, "http"),
    (HTTPS, "https"),
    (BEEF, "beef")
]

PROTOCOLS = {
    TELNET: "telnet",
    SSH: "ssh",
    HTTP: "http",
    HTTPS: "https",
    BEEF: "beef"
}

CLI_PROTOCOLS = {TELNET, SSH, BEEF}
HTTP_PROTOCOLS = {HTTP, HTTPS}
