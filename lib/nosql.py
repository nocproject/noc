## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MongoDB wrappers
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine import *
## NOC modules
import noc.settings

##
## Create database connection
## @todo: Handle tests
connect(noc.settings.NOSQL_DATABASE_NAME,
        noc.settings.NOSQL_DATABASE_USER,
        noc.settings.NOSQL_DATABASE_PASSWORD)
