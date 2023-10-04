# Фильтр VC (VC Filter)

Именованный фильтр VLANов (`VC Filter`) используется как фильтр вланов, в следующих настройках:

* Правила классификации интерфейсов [Interface Classification Rule](../interface/index.md#Interface Classification)
* Предоставляет категорию **vcfilter** в [Match Labels](../label/index.md#Match Labels)
* В правилах трансляции вланов Сегмента сети [Network Segment](../network-segment/index.md#VLAN Translation)

## Синтакис
`VC Filter` синтаксис выражения:

```
<vcfilter> ::= <item> [',' <vcfilter>]
<item> ::= <vlan> | <range>
<vlan> ::= [0-9]+
<range> ::= <vlan> '-' <vlan>
```

Примеры:

* `1-4095` - любой влан
* `100-200,300,1000` - подпадают номера VLANов с 100 до 200 (включительно), а также 300 и 1000
* `1` - только первый VLAN

## Настройки

Справочник меток расположен в разделе `VC (VC)` -> `Setup (Настройки)` -> `Фильтр VC (VC Filter)`.

![Форма редактирования VC Filter](vc-filter-any-vlan-form.png)

* **Имя** (`Name`) - наименование метки
* **Описание** (`Description`) - описание
* **Выражение** (`Expression`) - выражение набора влан
