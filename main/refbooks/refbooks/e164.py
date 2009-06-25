# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## E.164 Country Codes
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.main.refbooks.refbooks import RefBook,Field

##
## IEEE OUI Refbook
##
class E164(RefBook):
    name="E.164 Country Prefixes"
    description="E.164 Country Prefixes"
    downloader="CSV"
    download_url="http://update.nocproject.org/db/e164.csv"
    refresh_interval=90
    fields=[
        Field(name="Prefix",search_method="string"),
        Field(name="Country",search_method="substring"),
        ]