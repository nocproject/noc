# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# REST helper interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
# NOC modules
=======
##----------------------------------------------------------------------
## REST helper interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from noc.sa.interfaces.base import StringParameter


class DateTimeParameter(StringParameter):
    formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d"
    ]
    def clean(self, value):
        if value is None and self.default is not None:
            return self.default
        if isinstance(value, datetime.datetime):
            return value
        for f in self.formats:
            try:
                return datetime.datetime.strptime(value, f)
            except ValueError:
                pass
        self.raise_error("Invalid DateTime")


class DateParameter(DateTimeParameter):
    def clean(self, value):
        return super(DateParameter, self).clean(value).date()
