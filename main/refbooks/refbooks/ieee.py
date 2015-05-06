# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Built-in IEEE refbooks
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.main.refbooks.refbooks import RefBook,Field

##
## IEEE OUI Refbook
##
class IEEEOUI(RefBook):
    name="IEEE OUI"
    description="IEEE Assigned Organizational Units IDs. Used as first three octets of MAC Address"
    downloader="CSV"
    download_url="https://cdn.nocproject.org/refbook/ieee_oui.csv"
    refresh_interval=90
    fields=[
        Field(name="OUI",search_method="mac_3_octets_upper"),
        Field(name="ORG",search_method="substring"),
        ]