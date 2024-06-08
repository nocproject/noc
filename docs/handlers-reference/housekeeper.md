# Housekeeper

The interface is used to interact with the results of polling. Housekeeper runs at the end of the poll and
serves to manipulate the device (`ManagedObject`) based on the polling results.

Housekeeper is applied at the end of the [Discovery](../discovery-reference/box/hk.md) poll.

 
    housekeeper(check):
        Implements Housekeeper
    
        :param check: DiscoveryCheck 
        :returns: 

## Examples

### Assigning an Object Profile

Devices with [Capabilities](../caps-reference/index.md) `"BRAS | IPoE"` are assigned the object profile `bras`.

```python
    from noc.sa.models.managedobjectprofile import ManagedObjectProfile
    
    PROF_IPoE = ManagedObjectProfile.objects.get(name="bras")
    
    def housekeeper(check):
         object = check.object
         caps = object.get_caps()
         if caps.get("BRAS | IPoE") and object.object_profile != PROF_IPoE:
              object.object_profile = PROF_IPoE
              object.save()
```
