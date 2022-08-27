# UDLD

`Unidirectional Link Detection`. Изобретение Cisco - протокол по контролю состояния линка. 
Также позволяет видеть соседа (если сосед оборудование `Cisco`).


## Требования

* Скрипт [get_udld_neighbors](../../../../dev/sa/scripts/get_udld_neighbors.md)
* Возможность [Network UDLD](../../../../user/reference/caps/network/udld.md)
* Опрос UDLD включён в профиле объектов [Managed Object Profile](../../../../user/reference/concepts/managed-object-profile/index.md#Box(Полный_опрос))
* Метод UDLD в *Методах построения топологии* [Segment Profile](../../../../user/reference/concepts/network-segment-profile/index.md)
