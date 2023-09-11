# OAM check

`Operation, Administration, and Maintenance (OAM)`. Стандарт по мониторингу состояния линков, включается в том числе позволяет определять соседей и строить топологию. 

## Требования

* Скрипт [get_oam_status](../../../../dev/reference/scripts/get_oam_status.md)
* Возможность [Network OAM](../../../../user/reference/caps/network/oam.md)
* Опрос OAM включён в профиле объектов [Managed Object Profile](../../../../user/reference/concepts/managed-object-profile/index.md#Box(Полный_опрос))
* Метод OAM в *Методах построения топологии* [Segment Profile](../../../../user/reference/concepts/network-segment-profile/index.md)
