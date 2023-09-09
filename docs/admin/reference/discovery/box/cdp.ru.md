# cdp check

`Cisco Discovery Protocol`. Топологический протокол оборудования  `Cisco`. 
Также реализован у некоторых иных вендоров (`MikRotik`), но `ID` передаётся в каком-то своём формате поэтому построение линка, 
зачастую, невозможно. 

* Идентификатор оборудования: `FQDN`, `IP адрес` или серийный номер
* Идентификатор порта: имя


## Требования

* Скрипт [get_cdp_neighbors](../../../../dev/reference/scripts/get_cdp_neighbors.md)
* Возможность (`Capabilities`) [Network | CDP](../../../../user/reference/caps/network/cdp.md)
* Опрос CDP включён в профиле объектов [Managed Object Profile](../../../../user/reference/concepts/managed-object-profile/index.md#Box(Полный_опрос))
* Метод CDP в *Методах построения топологии* [Segment Profile](../../../../user/reference/concepts/network-segment-profile/index.md)
