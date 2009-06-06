# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ISO 3166 Country Codes
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.main.refbooks.refbooks import RefBook,Field

##
## IEEE OUI Refbook
##
class ISO3166(RefBook):
    name="ISO 3166 Country Codes"
    description="ISO 3166 Country Codes"
    downloader="CSV"
    download_url="http://update.nocproject.org/db/iso3166_1.csv"
    refresh_interval=90
    fields=[
        Field(name="Country",search_method="substring"),
        Field(name="Code",search_method="substring"),
        ]