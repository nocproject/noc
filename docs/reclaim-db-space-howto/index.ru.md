# How to Reclaim Database Space

Порой требуется уменьшить кол-во документов в коллекциях MongoDB для ускорения поиска и уменьшения размера индексов, а также возможно для увеличения скорости классификации аварий исключая слишком древние для переоткрытия. Также можно использовать для высвобождения места, занятого коллекциями.

## Очистка Архивных аварий (Archived alarms)
Механизм работы: Копирование всех архивных алармов, закрытых старше определённой даты, в архивные коллекции с последующим удалением из основной коллекции.

### Настройка:
В etc/settings.yml или в KV Consul (/Root/noc/bi/alarms_archive_policy) (убедиться, что он есть в [NOC_CONFIG](../config-reference/index.md#noc_config) в башне) следует указать настройки:

4m – 4 месяца, 5y – 5 лет, quarterly – как часто создавать новые коллекции. Можно поэкспериментировать.
Выставив quarterly мы получаем, что в течении года мы увидим 4 архивных коллекции по каждому кварталу. Как только дата закрытия аварии пересекает границу квартала - она попадает в следующую коллекцию.
Есть следующие варианты: {"weekly", "monthly", "quarterly", "yearly"}
```
bi:
  alarms_archive_policy: quarterly
  clean_delay_alarms: 4m
  clean_delay_reboots: 5y
  enable_alarms_archive: true
  enable_managedobjects: true
  enable_reboots: true
  enable_alarms: true
```
Убедиться, что в
```
./noc config dump bi
```

подгрузились верные значения переменных
Пример:
```
./noc config dump bi
 
bi:
  alarms_archive_batch_limit: 10000
  alarms_archive_policy: quarterly
  chunk_size: 3000
  clean_delay_alarms: 4m
  clean_delay_reboots: 5y
  enable_alarms: true
  enable_alarms_archive: true
  enable_managedobjects: true
  enable_reboots: true
  extract_delay_alarms: 1h
  extract_delay_reboots: 1h
  extract_window: 1d
  language: en
  query_threads: 10
  reboot_interval: 1M
```
```./noc bi clean```  -- тестовый запуск без удаления данных.

При запуске без ключа ```--force```:
```
./noc bi clean
 
[reboots] Cleaned before 2013-11-13 11:32:58.424000 ...
[alarms] Cleaned before 2018-07-15 11:51:58.543000 ...
[managedobjects] Cleaned before 2018-09-13 12:00:07.948000 ...
```
***Внимание***: данные БУДУТ скопированы в архивные коллекции `alarms.y*` , но НЕ БУДУТ удалены из основной коллекции `noc.alarms.archived`.

Если вы запустили тестовый запуск, почистите потом все архивные коллекции `alarms.y20XX*` чтобы при повторном запуске не было проблем.

```./noc bi clean --force``` реальное перемещение данных
При реальном запуске после показа дат будет обратный отсчёт до внесения изменений. У вас есть время одуматься.
```
./noc bi clean --force
 
[reboots] Cleaned before 2013-11-13 11:32:58.424000 ...
All data before reboots from collection 2013-11-13 11:32:58.424000 will be Remove..
 
9
 
8
```

Как убедиться, что всё сработало:
```
./noc mongo – идём в монгу
 
show collections; – смотрим список коллекций, убеждаемся, что там нет коллекций, которые начинаются на `alarms.y` --если они там есть, значит вы уже пользовались командой.
 
db.noc.alarms.archived.find().sort({"timestamp": 1}).limit(1)  – запоминаем `"clear_timestamp"` – первый закрытый аларм. После чистки время должно быть бОльше времени очистки.
 
db.noc.alarms.archived.count() – сколько сейчас документов в коллекции архивных алармов. Запоминаем и после удаления проверяем, что кол-во уменьшилось.
 
db.alarms.y2018_quarter3.count() – сколько документов в архивной коллекции
 
Далее ./noc bi clean --force и после этого анализируем коллекции в mongo.
```
***Внимание***:Если вам захочется дропнуть архивные коллекции – дропать можно все `alarm.y*` КРОМЕ ПОСЛЕДНЕЙ, туда возможно ещё будут записаны алармы.

## Очистка событий (events)
***Механизм работы***: Будет дропнуты все события старше 4-х недель. Это дефолт, можно передать свой параметр через ```--before```, смотри код.

```
./noc events clean --before 2019-11-27
or 
./noc events clean --before-days 365
```

### Настройка:
```./noc events clean``` покажет сколько событий ***может быть (но не будет)*** дропнуто в периоды:
``` 
Before is not set, use default
 
[events] Cleaned before 2018-10-15 15:12:35.931421 ...
Interval: 2018-04-30 13:10:59, 2018-05-07 13:10:59; Count: 1
Interval: 2018-05-07 13:10:59, 2018-05-14 13:10:59; Count: 4
------------////////////////////////--------------------------
Interval: 2018-10-08 13:10:59, 2018-10-15 13:10:59; Count: 21131
Interval: 2018-10-15 13:10:59, 2018-10-22 13:10:59; Count: 20412

./noc events clean --force
./noc events clean --force --before 2019-11-07
```
К примеру До и После очистки:
``` 
./noc mongo – идём в монгу
 
db.noc.events.active.count()
562620
 
db.noc.events.active.count()
427573
```
Всё готово.

## Очистка коллекций датастримов (datastream)

***Механизм работы***: Будет удалены все документы в коллекции старше параметра **N**_ttl, указанного в настройках секции datastream
Если указан 0, удаления не будет.
Посмотреть текущие настройки: `./noc config dump datastream`

***Использование***: 
`./noc datastream clean --datastream alarm` , где `alarm` название датастрима.

Проверка работы:

```
./noc mongo
 db.ds_alarm.stats()
До:
	"ns" : "noc.ds_alarm",
	"size" : 9083632515,
	"count" : 4675331,
	"avgObjSize" : 1942,
	"storageSize" : 1519890432,
	"freeStorageSize" : 9973760,

./noc datastream clean --datastream alarm

После:
	"ns" : "noc.ds_alarm",
	"size" : 766903963,
	"count" : 389807,
	"avgObjSize" : 1967,
	"storageSize" : 1546620928,
	"freeStorageSize" : 1415208960,

```
Размер коллекции уменьшился, но на диске места не освободилось из-за особенностей работы MongoDB.

## MongoDB Compact

С версии 4.4 возможно проводить компакт коллекций и вернуть место, помеченное как свободное.

**Внимание**: Разработчики рекомендуют делать бекапы БД ДО проведения такой операции.

***Пример***
```
use noc
db.runCommand({ compact: "ds_alarm", force:true })

{
	"bytesFreed" : 1619468288,
	"ok" : 1,
	"$clusterTime" : {
		"clusterTime" : Timestamp(1648810501, 640),
		"signature" : {
			"hash" : BinData(0,"bVXq9xHXqN3VNYj/qnh/z1ZBzkQ="),
			"keyId" : NumberLong("7029149395098533889")
		}
	},
	"operationTime" : Timestamp(1648810501, 639)
}
```
Было освобождено 1.5Гб. В критичных ситуациях может помочь.
Также наиболее результативными будут компакты следующих коллекций:
```
noc.alarms.archived
noc.events.active
и ds_* при условии частого обновления данных

```

# PostgreSQL

Удаление архивных вещей снаружи не требуется. Возможно стоит следить за логами БД

# ClickHouse

Механизм очистки архивных данных реализован на основе настройки TTL в интерфейсе `Main/Setup/CH Policies`

**Настройка**
Пример таблиц для настройки:

```
raw_cpu
raw_interface
raw_mac
raw_ping
raw_alarms
raw_memory
raw_reboots
raw_environment
```
TTL по своему усмотрению, для `raw_mac` достаточно `30`

**Пример использования**

`./noc ch-policy apply --host 0.0.0.0` - выведет объём данных, которые будут удалены.

Ключ `--approve` удалит данные:
`noc ch-policy apply --host 0.0.0.0 --approve`
