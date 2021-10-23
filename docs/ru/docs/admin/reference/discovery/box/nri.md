# nri check

Построение линков по информации из внешней системы. 
Механизм интеграции с внешней системой [Remote System](../../../../user/reference/concepts/remote-system/index.md) позволяет выгружать информацию по линкам и по ней строить линки в НОКе. 
Для этого необходимо реализация выгрузке в адаптере `ETL` и адаптеры маппинга портов (`portmapper`).

## Requirements

* Опрос NRI и `NRI Portmapper` включёны в профиле объектов [Managed Object Profile](../../../../user/reference/concepts/managed-object-profile/index.md#Box(Полный_опрос))
* Реализованный `Pormapper` для внешней системы