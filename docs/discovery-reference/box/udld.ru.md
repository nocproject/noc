# UDLD

`Unidirectional Link Detection`. Изобретение Cisco - протокол по контролю состояния линка. 
Также позволяет видеть соседа (если сосед оборудование `Cisco`).


## Требования

* Скрипт [get_udld_neighbors](../../scripts-reference/get_udld_neighbors.md)
* Возможность [Network UDLD](../../caps-reference/network.md#network-udld)
* Опрос UDLD включён в профиле объектов [Managed Object Profile](../../concepts/managed-object-profile/index.md#Box(Полный_опрос))
* Метод UDLD в *Методах построения топологии* [Segment Profile](../../concepts/network-segment-profile/index.md)
