# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# ISO 3166 Country Codes
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
## ISO 3166 Country Codes
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.main.refbooks.refbooks import RefBook,Field

##
## IEEE OUI Refbook
##
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
class ISO3166(RefBook):
    name="ISO 3166 Country Codes"
    description="ISO 3166 Country Codes"
    downloader="CSV"
    download_url="https://cdn.nocproject.org/refbook/iso3166_1.csv"
    refresh_interval=90
    fields=[
        Field(name="Country",search_method="substring"),
        Field(name="Code",search_method="substring"),
<<<<<<< HEAD
        ]
=======
        ]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
