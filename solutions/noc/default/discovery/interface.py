## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## interface_discovery helpers
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.main.models import PyRule
from noc.inv.models.interfaceclassificationrule import InterfaceClassificationRule
from noc.settings import config


_get_interface_profile = None


def prepare_classification():
    global _get_interface_profile

    p = config.get("interface_discovery", "classification_pyrule")
    if p:
        # Use pyRule
        r = list(PyRule.objects.filter(name=p,
                interface="IInterfaceClassification"))
        if r:
            # logging.info("Enabling interface classification pyRule '%s'" % p)
            _get_interface_profile = r[0]
        else:
            #logging.error("Interface classification pyRule '%s' is not found. Ignoring" % p)
            pass
    elif InterfaceClassificationRule.objects.filter(is_active=True).count():
        # Load rules
        #logging.info("Compiling interface classification rules:\n"
        #               "-----[CODE]-----\n%s\n-----[END]-----" %\
        #               InterfaceClassificationRule.get_classificator_code())
        _get_interface_profile = InterfaceClassificationRule.get_classificator()


def get_interface_profile(interface):
    """
    Perform interface classification and return interface profile name.
    Can be redefined in custom solutions
    :param interface: Interface instance
    :returns: profile name or None
    """
    if _get_interface_profile:
        return _get_interface_profile(interface=interface)
    else:
        return None

## Compile classification rule
prepare_classification()