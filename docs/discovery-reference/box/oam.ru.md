# OAM check

`Operation, Administration, and Maintenance (OAM)`. Стандарт по мониторингу состояния линков, включается в том числе позволяет определять соседей и строить топологию. 

## Требования

* Скрипт [get_oam_status](../../scripts-reference/get_oam_status.md)
* Возможность [Network OAM](../../caps-reference/network.md#network-oam)
* Опрос OAM включён в профиле объектов [Managed Object Profile](../../concepts/managed-object-profile/index.md#Box(Полный_опрос))
* Метод OAM в *Методах построения топологии* [Segment Profile](../../concepts/network-segment-profile/index.md)
