# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Built-in Q.931 refbooks
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.main.refbooks.refbooks import RefBook,Field

##
## IEEE OUI Refbook
##
class Q931CC(RefBook):
    name="Q.931 Call Clearings"
    description="Q.931 ISDN Call Clearings"
    downloader="CSV"
    download_url="http://update.nocproject.org/db/q931_call_clearing.csv"
    refresh_interval=90
    fields=[
        Field(name="DEC"),
        Field(name="HEX"),
        Field(name="Description",search_method="substring"),
        ]