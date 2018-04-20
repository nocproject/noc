# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# IGetDOMStatus interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.interface.base import BaseInterface
from base import (ListOfParameter, InterfaceNameParameter,
                  DictParameter, FloatParameter, NoneParameter)


class IGetDOMStatus(BaseInterface):
=======
##----------------------------------------------------------------------
## IGetDOMStatus interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import *


class IGetDOMStatus(Interface):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    """
    Get Digital Optical Monitoring status

    >>> IGetDOMStatus().clean_result([{"interface": "Gi 0/1",\
                                       "optical_tx_dbm": "-2.5",\
                                       "optical_rx_dbm": None}])
    [{'interface': 'Gi 0/1', 'optical_rx_dbm': None, 'optical_tx_dbm': -2.5}]
    """
    interface = InterfaceNameParameter(required=False)
    returns = ListOfParameter(element=DictParameter(attrs={
        "interface": InterfaceNameParameter(),
<<<<<<< HEAD
        "temp_c": (NoneParameter(required=False) |
                   FloatParameter(required=False)),
        "voltage_v": (NoneParameter(required=False) |
                      FloatParameter(required=False)),
        "current_ma": (NoneParameter(required=False) |
                       FloatParameter(required=False)),
        "optical_rx_dbm": (NoneParameter(required=False) |
                           FloatParameter(required=False)),
        "optical_tx_dbm": (NoneParameter(required=False) |
                           FloatParameter(required=False)),
=======
        "temp_c": (FloatParameter(required=False) |
                   NoneParameter(required=False)),
        "voltage_v": (FloatParameter(required=False) |
                      NoneParameter(required=False)),
        "current_ma": (FloatParameter(required=False) |
                       NoneParameter(required=False)),
        "optical_rx_dbm": (FloatParameter(required=False) |
                           NoneParameter(required=False)),
        "optical_tx_dbm": (FloatParameter(required=False) |
                           NoneParameter(required=False)),
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        }))
    preview = "NOC.sa.managedobject.scripts.ShowDomStatus"
