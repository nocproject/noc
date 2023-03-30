

# get_arp

<!-- prettier-ignore -->
!!! todo

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

## Input Arguments

## Result

## Examples

## Supported Profiles

{{ script_profiles("get_arp") }}

## Used in
