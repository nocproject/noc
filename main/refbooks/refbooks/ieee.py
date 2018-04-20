# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Built-in IEEE refbooks
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
from noc.main.refbooks.refbooks import RefBook,Field

#
# IEEE OUI Refbook
#
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
class IEEEOUI(RefBook):
    name="IEEE OUI"
    description="IEEE Assigned Organizational Units IDs. Used as first three octets of MAC Address"
    downloader="CSV"
    download_url="https://cdn.nocproject.org/refbook/ieee_oui.csv"
    refresh_interval=90
    fields=[
        Field(name="OUI",search_method="mac_3_octets_upper"),
        Field(name="ORG",search_method="substring"),
<<<<<<< HEAD
        ]
=======
        ]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
