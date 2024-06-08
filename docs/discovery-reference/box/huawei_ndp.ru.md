# Huawei NDP

`Huawei Network (Topology) Discovery Protocol` . Клон `CDP` от Huawei (не путать с NDP из IPv6). Работает только между устройствами `Huawei`, есть режим совместимости с `CDP`

## Требования

* Скрипт [get_huawei_ndp_neighbors](../../scripts-reference/get_huawei_ndp_neighbors.md)
* Возможность [Huawei NDP caps](../../caps-reference/huawei.md#huawei-ndp)
* Опрос `Huawei NDP` включён в профиле объектов [Managed Object Profile](../../concepts/managed-object-profile/index.md#Box(Полный_опрос))
* Метод `Huawei NDP` в *Методах построения топологии* [Segment Profile](../../concepts/network-segment-profile/index.md)
