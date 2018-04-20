# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IGetVerson interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

<<<<<<< HEAD
# Python modules
from __future__ import absolute_import
# NOC modules
from noc.core.interface.base import BaseInterface
from .base import DictParameter, StringParameter


class IGetVersion(BaseInterface):
=======

class IGetVersion(Interface):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    returns = DictParameter(attrs={
        "vendor": StringParameter(),
        "platform": StringParameter(),
        "version": StringParameter(),
<<<<<<< HEAD
        "image": StringParameter(required=False),
=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        "attributes": DictParameter(required=False)
    })
