

# get_bfd_sessions

<!-- prettier-ignore -->
!!! todo

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

## Input Arguments

## Result

## Examples

## Supported Profiles

{{ script_profiles("get_bfd_sessions") }}

## Used in
-------
* [Discovery Box BFD](../../../admin/reference/discovery/box/bfd.md)
