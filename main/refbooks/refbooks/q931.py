# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Built-in Q.931 refbooks
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
## Built-in Q.931 refbooks
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.main.refbooks.refbooks import RefBook,Field

##
## IEEE OUI Refbook
##
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
class Q931CC(RefBook):
    name="Q.931 Call Clearings"
    description="Q.931 ISDN Call Clearings"
    downloader="CSV"
    download_url="https://cdn.nocproject.org/refbook/q931_call_clearing.csv"
    refresh_interval=90
    fields=[
        Field(name="DEC"),
        Field(name="HEX"),
        Field(name="Description",search_method="substring"),
<<<<<<< HEAD
        ]
=======
        ]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
