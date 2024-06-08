# REP опрос

[Resilient Ethernet Protocol](https://www.cisco.com/c/en/us/support/docs/lan-switching/ethernet/116384-technote-rep-00.html). 
Изобретение Cisco - протокол для замены `STP` в кольцевых топологиях. В выводе присутствуют все участники кольца с интерфейсами:

```
SwitchA#show rep topology
REP Segment 1
BridgeName       PortName   edge Role
---------------- ---------- ---- ----
SwitchA          Fa0/2      Pri  Alt 
SwitchC          Fa1/0/23        Open
SwitchC          Fa1/0/2         Open
SwitchD          Fa0/23          Open
SwitchD          Fa0/2           Open
SwitchB          Fa1/0/23   Sec  Open
```

* Скрипт: `get_rep_neighbors`
* Возможность (`Capabilities`): `Network | REP`
* Опция `Object Profile` (Профиля объектов): REP
* Опция `Segment Profile` (Профиля сегмента): REP

## Requirements

* Скрипт [get_rep_neighbors](../../scripts-reference/get_rep_topology.md)
* Возможность (`Capabilities`) [Network REP caps](../../caps-reference/network.md#network-rep)
* Опрос CDP включён в профиле объектов [Managed Object Profile](../../concepts/managed-object-profile/index.md#Box(Полный_опрос))
* Опция REP в *Методах построения топологии* [Segment Profile](../../concepts/network-segment-profile/index.md)