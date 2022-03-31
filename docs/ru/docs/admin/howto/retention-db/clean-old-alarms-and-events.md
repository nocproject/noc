# How to clean old Alarms and Events
Порой требуется уменьшить  кол-во документов в коллекциях mongo для ускорения поиска и уменьшения размера индексов, а также возможно увеличение скорости классификации аварий исключая слишком древние для переоткрытия. Также можно использовать для высвобождения места, занятого монгой.

## Очистка Архивных аварий (Archived alarms)
Механизм работы: Копирование всех архивных алармов, закрытых старше определённой даты, в архивные коллекции с последующим удалением из основной коллекции.

### Настройка:
В etc/settings.yml или в KV Consul (/Root/noc/bi/alarms_archive_policy) (убедиться, что он есть в [PATH]: https://docs.getnoc.com/master/[en/ru]/admin/reference/config/#noc_config в башне) следует указать настройки:

4m – 4 месяца, 5y – 5 лет, quarterly – как часто создавать новые коллекции. Можно поэкспериментировать.
Выставив quarterly мы получаем, что в течении года мы увидим 4 архивных коллекции по каждому кварталу. Как только дата закрытия аварии пересекает границу квартала - она попадает в следующую коллекцию
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
```./noc config dump bi```  подгрузились верные значения переменных
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

```./noc events clean --before 2019-11-07```

### Настройка:
```./noc events clean``` покажет сколько событий ***будет (но не будет удалено)*** дропнуто в периоды:
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
