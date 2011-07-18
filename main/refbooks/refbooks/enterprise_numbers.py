# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IANA enterprise numbers refbook
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.main.refbooks.refbooks import RefBook, Field


class ISO3166(RefBook):
    name = "SMI Network Management Private Enterprise Codes"
    description = "iso.org.dod.internet.private.enterprise (1.3.6.1.4.1)"
    downloader = "CSV"
    download_url = "http://update.nocproject.org/db/enterprise-numbers.csv"
    refresh_interval = 90
    fields = [
        Field(name="Number", search_method="string"),
        Field(name="Organization", search_method="substring"),
        ]
