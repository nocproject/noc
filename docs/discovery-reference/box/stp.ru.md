# STP

`Spanning Tree Protocol`. Не топологический протокол, но при обмене информацией передаёт номер назначенного порта. 
Это позволяет построить линк снизу вверх (в сторону рута). 
Номер назначенного порта (`Desg. Port`) в выводе отдают не все устройства, в частности у `DLink` он отсутствует.

* Скрипт: `get_stp_neighbors`
* Возможность (`Capabilities`): `Network | STP`
* Опция `Object Profile` (Профиля объектов): STP
* Опция `Segment Profile` (Профиля сегмента): STP

Пример вывода с оборудования протоколу STP. Порт в сторону вышестоящей железки с `ID` `0025-9922-1122` и портом `26`.

```
----[Port25(XGigabitEthernet0/1/1)][FORWARDING]----
 Port Protocol       :enabled
 Port Role           :Root Port
 Port Priority       :128
 Port Cost(Dot1T )   :Config=auto / Active=2000
 Desg. Bridge/Port   :32768.0025-9922-1122 / 128.26
 Port Edged          :Config=default / Active=disabled
 Point-to-point      :Config=auto / Active=true
 Transit Limit       :147 packets/hello-time
 Protection Type     :None
```

## Требования

* Скрипт [get_spanning_tree](../../scripts-reference/get_spanning_tree.md)
* Возможность [Network STP](../../caps-reference/network.md#network-stp)
* Опрос STP включён в профиле объектов [Managed Object Profile](../../concepts/managed-object-profile/index.md#Box(Полный_опрос))
* Метод STP в *Методах построения топологии* [Segment Profile](../../concepts/network-segment-profile/index.md)
