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
расположенных в меню `Fault Management -> Setup -> Classification Rule`.

События в классификатор поступают по очереди [events](../../../dev/reference/streams/events.md). 
Для поступившего события происходит поиск подходящего правила в порядке возрастания приоритета.

Для каждого входящего события правила просматриваются в порядке возрастания первое совпадение выставляет класс события.

Структура правила классификации

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

