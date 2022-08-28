# Housekeeper


Интерфейс для взаимодействия с результатами опроса. Housekeeper запускается в конце опроса и
служит для манипуляции с устройством (`ManagedObject`) по результатам опроса. 

Housekeeper применяется в конце опроса [Discovery](../../admin/reference/discovery/box/hk.md).

 
    housekeeper(check):
        Implements Housekeeper
    
        :param check: DiscoveryCheck 
        :returns: 

## Примеры

### Назначение профиля объекта 

Устройствам с [Capabilities](../../user/reference/caps/index.md) `"BRAS | IPoE"` назначается профиль объекта `bras`.

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
