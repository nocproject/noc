# Fault Management


Primary task of the Fault Management is to collect and process events. 
Events are created as result of network activity, user operations, clients activity, equipment faults etc. 
Working network can generate thousands of events every minute. 
FM module allows to collect them, classify, assign priorities, correlate events and automatically determine root cause of failure. 
System supports life cycle of events ensuring no important events left unnoticed or unhandled.

## Возможности по работе со сбоями

Основная задача `Fault Management` приём, обработка и реакция на события. 
События (`Event`) могут в результате работы оборудования, действий пользователя, ошибок оборудования и других. 
Работающая сеть может создавать тысячи событий в минуту. Модуль `FM` позволяет в режиме реального времени:

* Приём сообщений о событиях из различных источников:
    * ICMP - проверка доступности устройства
    * SNMP - приём `SNMP Trap`
    * Syslog - приём `Syslog` с устройства
    * Пороги по метрикам (`Metric Threshold`)
    * Результаты опроса устройства (`Discovery`)  
    * Синхронизация сообщений с устройством
* Классификация событий на основе правил
* Обогащение событий данными из системы
* Создание на основе событий аварийного сообщения
* Корреляция аварий и автоматическое определение первопричины (`Root Cause`)
* Реакция на аварию:
    * Отправка уведомления
    * Запуск диагностики
    * Эскалация
* Группировка аварий
* Работа с авариями в интерфейсе пользователя
* Аналитика по авариям на основе подсистемы BI

При работе с событиями используются термины:

* Событие (`Event`) - 
* Класс события `Event Class` - значение события
* Классификация события (`Event Classification`) - процесс анализа события, завершается присвоением класса
* Авария (`Alarm`) - Событие, требующее реакции
* Класс аварии `Alarm Class` - значение аварии
* Корреляция аварии `Alarm Correlation` - процесс определение первопричины аварии
* Определение первопричины (`RCS`, `Root-cause analyses`)

! конвеер обработки событий

## Сбор событий

События поступают в систему различными путями. Источниками могут быть отдельные как сервисы (коллекторы) так и 
внутренни события системы. Рассмотрим доступные источники событий:

| Источник | Активный | Протокол | Класс события | класс аварии | 
|   ---    |  -----    | ---     | ---    | -------      |
| [ping](../../../admin/reference/services/ping.md)  | v  | ICMP  | - | `NOC || Managed Object || Ping Failed`  | 
| [trapcollector](../../../admin/reference/services/trapcollector.md) | x | SNMP | By Rule | By Rule |
| [syslogcollector](../../../admin/reference/services/syslogcollector.md) | x | Syslog | By Rule | By Rule |
| [Metric Threshold](../../../admin/reference/discovery/periodic/metrics.md) | v | -    | [Threshold Profile](../../../user/reference/concepts/threshold-profile/index.md) | [Threshold Profile](../../../user/reference/concepts/threshold-profile/index.md) | 
| [Config Validation](../../../admin/reference/discovery/box/config.md) | v | - | [Config Validation Rules](../../../user/background/configuration-management/index.md#Создание%20политики%20валидации%20на%20основе%20запросов%20ConfDB) | 
| [Alarm Discovery](../../../admin/reference/discovery/box/alarm.md) | v | CLI | By Rule | By Rule |
| [Discovery](../../../admin/reference/discovery/box/index.md) | v | CLI | - | - | 


## Обработка событий

Дальнейшая обработка события может пойти двумя путями:

1. Для событий из устройств это `Классификатор` -> `Коррелятор`
2. Внутренние события системы направляются непосредственно в `Коррелятор`

### Классификация событий

Задача этапа классификации определить какому классу [Event Class](../../reference/concepts/event-class/index.md) 
принадлежит поступившее событие и действовать согласно указанным в нём настройкам. Для определения класса события 
используется набор правил классификации [Event Classification Rule](../../reference/concepts/event-classification-rule/index.md), 
расположенных в меню `Управление авариями (Fault Management) -> Настройка (Setup) -> Правила классификации (Classification Rule)`.

События в классификатор поступают по очереди [events](../../../dev/reference/streams/events.md). Передаются в формате `JSON` 
и отличаются содержимым поля `data`, которое заполняется данными на источнике:

* `source`- источник события:
    * `syslog` - коллектор `Syslog`
    * `SNMP Trap` - коллектор `SNMP Trap`
    * `system` - некоторые системные сервисы (`ping`, `discovery`)
    * `other` - неизвестный источник
* `collector` - пул [Pool](../../reference/concepts/pool/index.md)
* Специфичные данные (зависят от источника):
    * `message` - содежит сообщение `syslog`
    * `1.3.6.1.6.3.1.1.4.1.0` (`snmpTrapOID`) - OID 
    * `...`

Пример события `Syslog`:
```json
{"ts":1637243036,"object":"61088","data":{"source":"syslog","collector":"default","message":"%AAA-I-DISCONNECT: User CLI session for user user1 over telnet , source Y.Y.Y.Y destination  X.X.XX.X  TERMINATED."}}

```

Пример события `SNMP Trap`:

```json

{"ts":1637243038,"object":"45324","data":{"source":"SNMP Trap","collector":"default","1.3.6.1.2.1.1.3.0":"973858","1.3.6.1.6.3.1.1.4.1.0":"1.0.8802.1.1.2.0.0.1","1.0.8802.1.1.2.1.2.2":"3","1.0.8802.1.1.2.1.2.3":"1","1.0.8802.1.1.2.1.2.4":"0","1.0.8802.1.1.2.1.2.5":"1"}}
```

Для поступившего события происходит поиск подходящего правила на основе содержимого поля `data` в порядке возрастания приоритета. 
При наличии `MIB` для сообщений `SNMP Trap` числовые обозначения будут сконвертированы в текстовые представления. 
Это позволит использовать в правилах имена переменных из `MIB`.

Структура правила классификации

! переменные по умолчанию
source
profile

Формат сообщения `Syslog`

Формат события `SNMP Trap`


Доступные действия
* Log
* Drop
* Archive

Использование MIB

#### Правила размещения (Disposition Rule)

Дальнейшая судьба события определяется в настройках `Disposition Rule` класса события. 
Это своего рода таблица маршрутизации.

#### Игнорирование событий

Для ограждения системы от особо разговорчивых устройств можно настроить правила игнорированая событий. Они раздлеются на 
шаблоны и правила. Разница в том, что шаблоны действуют до классификации события на уровне входящих сообщений, а правила 
после того как событию присвоен класс

Шаблоны проверяют на совпадение переменную `message` для сообщений `Syslog` и переменную `1.3.6.1.6.3.1.1.4.1.0` (`snmpTrapOID`) для `SNMP Trap`
Ignore Event Rules
? Вынести в concepts
Ignore Patterns

#### Дедупликация и подавление повторов (Deduplicate and Suppression)

#### Время жизни события (TTL)

### Корреляция событий

Основная задача коррелятора, это сокращение числа событий путём установления первопричины (корреляции) и группировки. 
Это позволяет сигнализировать оператору только о том, на что стоит обратить внимание, отсеивая менее важное путём выставление важности (`severity`). 

События в коррелятор [correlator](../../../admin/reference/services/correlator.md) поступают по
очереди [dispose](../../../dev/reference/streams/dispose.md) 

Коррелятор ищет связи между событиями их разных источников, осуществляет их корреляцию и группировку, 
получая на выходе аварийные события - Аварии


## Визуализация

