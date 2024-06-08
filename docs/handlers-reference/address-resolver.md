# Address Resolver

The interface is used for resolving the IP address of a device (`ManagedObject`) based on the `FQDN` field. The address resolution is triggered before polling and attempts to determine the IP address through DNS. The handler implements its own algorithm for determining the IP address of the device.

The Address Resolver is applied at the beginning of the [Discovery](../discovery-reference/box/index.md) process.


    address_resolver(fqdn):
        Implements Address Resolver
    
        :param fqdn: Managed Object Instance FQDN field 
        :returns: 

## Examples

### Resolving Address from a Local File

At the start of the polling process, it checks a local file (which should be located on the same host as the `Discovery` process) and returns the discovered IP address.

```python
    import os

    FILENAME = "/tmp/device_addresses.txt"
    
    def address_resolver(fqdn):
        if os.path.exists(FILENAME):
            with open(FILENAME, "r") as f:
                for ll in f.readlines():
                    address, host = ll.split(",")
                    if fqdn.startswith(host):
                        return address

```
