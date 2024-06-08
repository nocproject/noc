# LACP

`Link Aggregation Control Protocol`. Протокол агрегации линков, также может быть использован для определения соседей.

## Требования

* Скрипт [get_lacp_neighbors](../../scripts-reference/get_lacp_neighbors.md)
* Возможность [Network LACP](../../caps-reference/network.md#network-lacp)
* Опрос LACP включён в профиле объектов [Managed Object Profile](../../concepts/managed-object-profile/index.md#Box(Полный_опрос))
* Метод LACP в *Методах построения топологии* [Segment Profile](../../concepts/network-segment-profile/index.md)

Возможен случай когда с одной стороны один порт находится в отключённом состоянии (обычно, это делается для `холодного резерва`). 
В этом случае для построения линка необходимо активировать опцию `Разрешить соединение LAG<-> physical` (`Allow LAG Mismatch`) в профиле интерфейса (`Interface Profile`).
