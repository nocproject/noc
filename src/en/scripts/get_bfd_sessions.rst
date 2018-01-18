.. _script-get_bfd_sessions:

=======================================
get_bfd_sessions
=======================================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

.. todo::
    Describe get_bfd_sessions script

::

    returns = DictListParameter(attrs={
        "local_address": IPParameter(required=False),
        "remote_address": IPParameter(),
        "local_interface": InterfaceNameParameter(),
        "local_discriminator": IntParameter(),
        "remote_discriminator": IntParameter(),
        "state": StringParameter(choices=["UP", "DOWN"]),
        "clients": ListOfParameter(element=StringParameter(choices=[
            "L2", "RSVP", "ISIS", "OSPF", "BGP", "EIGRP", "PIM"
        ])),
        # Transmit interval, microseconds
        "tx_interval": IntParameter(),
        "multiplier": IntParameter(),
        # Detection time, microseconds
        "detect_time": IntParameter()
    })

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
