# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# E.164 Country Codes
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
## E.164 Country Codes
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.main.refbooks.refbooks import RefBook,Field

##
## IEEE OUI Refbook
##
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
class E164(RefBook):
    name="E.164 Country Prefixes"
    description="E.164 Country Prefixes"
    downloader="CSV"
    download_url="https://cdn.nocproject.org/refbook/e164.csv"
    refresh_interval=90
    fields=[
        Field(name="Prefix",search_method="string"),
        Field(name="Country",search_method="substring"),
<<<<<<< HEAD
        ]
=======
        ]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
