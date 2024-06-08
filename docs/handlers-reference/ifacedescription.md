# Interface Description

This interface is used for interacting with the polling of links based on interface descriptions (`Description`). It is launched as part of the `ifdescr` polling process if it is selected in the [ManagedObjectProfile](../concepts/managed-object-profile/index.md) settings, under the `ifdescr_handler` option.

Interface Description is applied during the [IfDescr](../discovery-reference/box/ifdesc.md) polling process.

 
    interface_description(managed_object, interface):
        Implements Interace Description

        :param managed_object: Managed Object instance
        :param interface: Interface instance
        :returns: 

## Examples

### Building Links Based on Hostname in Descriptions

Allows linking (`Linking`) devices in which the descriptions of interfaces contain the `hostname` of a neighbor. 
`device1 - hostname2 <-> hostname1 device2`. Returns the neighbor's interface to which the local interface should be connected.

```python
    # Python modules
    import re
    import logging
    
    # NOC modules
    from noc.inv.models.discoveryid import DiscoveryID
    from noc.inv.models.interface import Interface
    from noc.sa.models.managedobject import ManagedObject
    
    logger = logging.getLogger()
    
    rx_hostname_default = re.compile(r"(?P<hostname>\S+)")
    
    
    def handler(o: ManagedObject, iface: Interface):
        logger.debug("Linking o %s, iface: %s" % (o, iface))
        rx_hostname = iface.profile.ifdesc_patterns or rx_hostname_default
        match = rx_hostname.search(iface.description)
        if match:
            # Find remote object by hostname
            rdid = DiscoveryID.objects.filter(hostname__icontains=match.group("hostname")).first()
            if not rdid:
                logger.warning("Not find remote object by hostname: %s", match.group("hostname"))
                logger.info("Not find remote_object")
                return None
            # Find local hostname on DiscoveryID
            ldid = DiscoveryID.objects.get(object=o.id)
            if not ldid.hostname:
                logger.info("Not find hostname for local Object")
                return None
            # Find RemoteInterface by description
            ri = Interface.objects.filter(
                managed_object=rdid.object, description__icontains=ldid.hostname
            ).first()
            if ri:
                return ri
            logger.info("Not find interface")
        return None
```
