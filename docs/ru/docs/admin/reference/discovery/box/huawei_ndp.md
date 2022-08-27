# Huawei NDP

`Huawei Network (Topology) Discovery Protocol` . Клон `CDP` от Huawei (не путать с NDP из IPv6). Работает только между устройствами `Huawei`, есть режим совместимости с `CDP`

## Требования

* Скрипт [get_huawei_ndp_neighbors](../../../../dev/sa/scripts/get_huawei_ndp_neighbors.md)
* Возможность [Huawei NDP caps](../../../../user/reference/caps/huawei/ndp.md)
* Опрос `Huawei NDP` включён в профиле объектов [Managed Object Profile](../../../../user/reference/concepts/managed-object-profile/index.md#Box(Полный_опрос))
* Метод `Huawei NDP` в *Методах построения топологии* [Segment Profile](../../../../user/reference/concepts/network-segment-profile/index.md)
