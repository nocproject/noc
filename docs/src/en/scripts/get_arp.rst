.. _script-get_arp:

=======================================
get_arp
=======================================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

.. todo::
    Describe get_arp script

::

    vrf = StringParameter(required=False)
    interface = InterfaceNameParameter(required=False)
    returns = ListOfParameter(element=DictParameter(attrs={
        "ip": IPv4Parameter(),
        # NONE for incomplete entries
        "mac": MACAddressParameter(required=False),
        # NONE for incomplete entries
        "interface": InterfaceNameParameter(required=False),
    }))

Input Arguments
---------------

Result
------

Examples
--------

Supported Profiles
------------------

Used in
-------
