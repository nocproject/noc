# nri check

Построение линков по информации из внешней системы. 
Механизм интеграции с внешней системой [Remote System](../../concepts/remote-system/index.md) позволяет выгружать информацию по линкам и по ней строить линки в НОКе. 
Для этого необходимо реализация выгрузке в адаптере [ETL](../../etl/index.md) и адаптеры привязки портов [portmapper](../../etl/index.md#Portmapper).

## Requirements

* Опрос NRI и `NRI Portmapper` включёны в профиле объектов [Managed Object Profile](../../concepts/managed-object-profile/index.md#Box(Полный_опрос))
* Реализованный [Portmapper](../../etl/index.md#portmapper) для внешней системы