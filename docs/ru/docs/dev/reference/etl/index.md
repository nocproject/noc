# ETL

## Описание механизма



## Поддерживаемые модели

Для каждой из доступных сущностей системы описывается модель данных. В ней указывается поля и тип данных, доступные 
для выгрузки. Применяется библиотека [PyDantic](https://pydantic-docs.helpmanual.io). Модель расположены в папке `<noc_base>/core/etl/models`. 
Наследуются от базового класса `BaseModel`, для полей связи друг с другом используется тип `Reference`. Необязательные обозначаются как `Optional`:

```python

class AdministrativeDomain(BaseModel):
    id: str
    name: str
    parent: Optional[Reference["AdministrativeDomain"]]
    default_pool: Optional[str]

    _csv_fields = ["id", "name", "parent", "default_pool"]

```


## Адаптер выгрузки

Процедура извлечение данных из внешней системы и сопоставление их с моделью называется выгрузка (`extract`). 
Для её работы реализуется адаптер, в котором запрошенная информация транслируется в формат модели данных. Адаптер 
состоит из внешней системы и классов, реализующих работу с одной моделью, образующих модуль. Пример:

```python

class ZBRemoteSystem(BaseRemoteSystem):
    """
    Базовый класс для Выгрузки.
    Для порядка описываем доступные для использования переменные, доступные в RemoteSystem Environment

    Configuration variables (Main -> Setup -> Remote System -> Environments)
    API_URL - URL zabbix web interface
    API_USER - username for ro access to device
    API_PASSWORD - password for user access
    GROUPS_FILTER - list groups for extract
    """

@ZBRemoteSystem.extractor
class ZBAdministrativeDomainExtractor(BaseExtractor):
    """
    Для извлечения зон ответственности (Administrative Domain).
    Поддерживается иерархия через указание родительской ЗО (Parent).
    При этом надо следить, чтоб родительские ЗО шли перед дочерними. Этого можно добиться через числовые ID
    """

    name = "administrativedomain"
    model = AdministrativeDomain
    data = [["zb.root", u"Заббикс", None]]


```

В начале описывается класс внешней системы - `ZBRemoteSystem`, он будет указан в ссылке на адаптер (`Handler`) настроек. 

::: noc.core.etl.remotesystem.base:BaseRemoteSystem

После идёт описание классов для работы с данными. Обязательно указывается какую *модель системы* и какую *модель данных* 
реализует класс.

::: noc.core.etl.extractor.base:BaseExtractor

В примере `ZBAdministrativeDomainExtractor` данные указаны в самом адаптере, реализация взаимодействия с внешней системой 
происходит в методе `extract`. Их коробки доступно несколько базовых реализаций адаптеров:
  * `Oracle SQL` - взаимодействие с `Oracle`
  * `MySQL` - организует взаимодействие с `MySQL` путём указания SQL запроса в аттрибуте `SQL`. Требует библиотеку `pymsql`
  * `FIAS`


Выгрузка запускается командой `./noc etl extract REMOTE_SYSTEM_NAME <EXTRACTOR_NAME>`, где:

* `REMOTE_SYSTEM_NAME` - имя внешней системы, указанное на предыдущем шаге
* `<EXTRACTOR_NAME>` - опциональное имя модели для загрузки

Данные укладываются в файл `import.csv` в папку, соответствующую имени модели системы
При этой команде произойдёт подключение к внешней системе, забор информации с неё и формирование файлов `import.csv` 
по пути: `etl_path/remote_system_name/loader_name/`


### Определение и проверка изменений

Проверка выгруженных данных выполняется командой `./noc etl check REMOTE_SYSTEM_NAME`. Происходит проверка файла `import.csv` на правильность структуры и связей.
Возможные ошибки:

* Отсутствует объект по ссылке
```
[noc.core.etl.loader.base] [RS|managedobject] ERROR: Field #4(administrative_domain) == 'administrativedomain' refers to non-existent record: 10106,mos-pma-pta-pta1-sw01#10106,True,,administrativedomain,default,!new,Generic.Host,zb.std.sw,,,2,192.168.3.2,,,,,,,ZB.AUTO,,
[noc.core.etl.loader.base] [RS|managedobject] ERROR: Field #4(administrative_domain) == 'administrativedomain' refers to non-existent record: 10107,mos-pma-lta-lta1-sw01#10107,True,,administrativedomain,default,!new,Generic.Host,zb.std.sw,,,2,192.168.3.4,,,,,,,ZB.AUTO,,
```
Расшифровывается, что поле `administrative_domain` ссылается на несуществующую запись в выгрузке с `administrativedomain` (на это указывает поле из `mapped_fields`) c ID `administrativedomain`
* Неправильный формат загрузки

Команда `./noc etl diff REMOTE_SYSTEM_NAME <ExtractorNAME>` позволяет увидеть разницу между последней успешной и текущей загрузками. В построчно формате с указателями:

* `/` - изменение
* `+` - новый объект
* `-` - удаление объекта

```
--- RS.admdiv
--- RS.networksegmentprofile
+ zb.default,zb.default
--- RS.networksegment
+ !new,,Новые,,zb.default
+ !rej,,Отсев,,zb.default
+ !tgfake,,tgfake,,zb.default
--- RS.container
+ 10107,ZabbixHost,PoP | Access,,0,60.646729,56.852081,Екатеринбург, ул. Мира 4
--- RS.resourcegroup
--- RS.managedobjectprofile
+ zb.core.sw,zb.core.sw,35
+ zb.std.sw,zb.std.sw,25
--- RS.administrativedomain
+ zb.root,Заббикс,
--- RS.authprofile
+ ZB.AUTO,ZB.AUTO,,S,,,,,
+ snmp.default,snmp.default,,G,,,,public,
--- RS.ttsystem
--- RS.managedobject
+ 10106,mos-pma-pta-pta1-sw01#10106,True,,zb.root,default,!new,Generic.Host,zb.std.sw,,,2,192.168.3.2,,,,,,,ZB.AUTO,
+ 10107,mos-pma-lta-lta1-sw01#10107,True,10107,zb.root,default,!new,Generic.Host,zb.std.sw,,,2,192.168.3.4,,,,,,,ZB.AUTO,
--- RS.link
--- RS.subscriber
--- RS.serviceprofile
--- RS.service

```

Есть дополнительный ключ - `summary` позволяет посмотреть суммарное число изменений:
`./noc etl diff --summary REMOTE_SYSTEM_NAME <ExtractorNAME>`
```
              Loader |      New |  Updated |  Deleted
              admdiv |        0 |        0 |        0
networksegmentprofile |        1 |        0 |        0
      networksegment |        3 |        0 |        0
           container |        1 |        0 |        0
       resourcegroup |        0 |        0 |        0
managedobjectprofile |        2 |        0 |        0

```


## Загрузчик


**Загрузка** заливка извлечённых данных в НОК выполняется командой `./noc etl load REMOTE_SYSTEM_NAME <loadername>`. Происходит применение изменений по следующем правилам:

* При создании объекта связка `ID внешней системы`: `ID Объекта в НОКе` записывается в файл `mappings.csv`, расположенным в папке загрузчика.
* при создании `PoP` по пути создаются объекты типа `контейнер`
* изменения считаются относительно данных `предыдущей` загрузки (!не данных в НОКе)
* удалённые объекты управления (`Managed Object`) переводятся в состояние `unmanaged`
* при удалении сегмента с находящиеся в нём объекты перемещаются в сегмент `ALL`

<!-- prettier-ignore -->
!!! warning
    Важно понимать, что изменения вычисляются относительно предыдущей загрузки (предыдущего состояния) из внешней системы. По этой причине, если внести изменения по полю в НОКе - загрузка эти изменения не откатит. Также, если потерять архивные файлы по последней выгузке, то все объекты будут пересозданы.


Адаптеры для загрузки (загрузчики), ответственные за создание  расположены в директории `core/etl/loader`. Разберём на примере `managedobject` (`core/etl/loader/managedobject.py`):

```python
class ManagedObjectLoader(BaseLoader):
    """
    Managed Object loader
    """
    name = "managedobject"  # Имя (Loader Name)
    model = ManagedObject   # NOC object Model (модель, создаваемая адаптером)
    fields = [        # Список полей, необходимых для создания
                     # объекта
        "id",            
        "name",
        "is_managed",
        "container",
        "administrative_domain",
        "pool",
        "segment",
        "profile",
        "object_profile",
        "static_client_groups",
        "static_service_groups",
        "scheme",
        "address",
        "port",
        "user",
        "password",
        "super_password",
        "snmp_ro",
        "description",
        "auth_profile",
        "tags",
        "tt_system",
        "tt_queue",
        "tt_system_id"
    ]

    mapped_fields = {  # карта связей полей с другими вгрузчиками (loader)
        "administrative_domain": "administrativedomain",
        "object_profile": "managedobjectprofile",
        "segment": "networksegment",
        "container": "container",
        "auth_profile": "authprofile",
        "tt_system": "ttsystem",
        "static_client_groups": "resourcegroup",
        "static_service_groups": "resourcegroup"
    }

```
Как видно выше `загрузчика` состоит из:

* `имени`
* указания на модель, загрузку которой он реализует
* `списка полей` необходимых для создания объекта
* `карты связи полей` применяется для ссылок на объекты, созданные другими загрузчиками
> Остановимся на карте связей подробнее. Для системы нормально, когда одни сущности связываются с другими. Это позволяет *не мешать всё в одну кучу*, по этой причине и существуют `карты связей` (`mappings map`). В примере указано что поле `object_profile` необходидо связать с вгрузчиком `managedobjectprofile`. Сама привязка идёт по полям ID (всегда первые в списке), а сам вгрузчик ищется по имени:
> 

Как видно, для `managedobjectprofile` достаточно 3 полей: `id`, `имя`, `уровень`. При этом, `карта связей` (`mapped_fields`) отсутствует.
```python
class ManagedObjectProfileLoader(BaseLoader):
    """
    Managed Object Profile loader
    """
    name = "managedobjectprofile"
    model = ManagedObjectProfile
    fields = [
        "id",
        "name",
        "level"
    ]
```

При работе с картами связей, необходимо помнить - что не все поля являются обязательными. Н-р для `managedobject` обязательными являются: `administrative_domain`, `object_profile`, `segment`
следовательно, для реализаци `адаптера выгрузки` объектов управления (`ManagedObject`), необходимо будет реализовать выгрузку для `administrativedomain`, `networksegment` и `managedobjectprofile`. Иначе при выполнении команды `./noc etl check` будет множество ошибок вида:
```
[noc.core.etl.loader.base] [RS|managedobject] ERROR: Field #4(administrative_domain) == 'administrativedomain' refers to non-existent record: 10106,mos-pma-pta-pta1-sw01#10106,True,,administrativedomain,default,!new,Generic.Host,zb.std.sw,,,2,192.168.3.2,,,,,,,ZB.AUTO,,
[noc.core.etl.loader.base] [RS|managedobject] ERROR: Field #4(administrative_domain) == 'administrativedomain' refers to non-existent record: 10107,mos-pma-lta-lta1-sw01#10107,True,10107,administrativedomain,default,!new,Generic.Host,zb.std.sw,,,2,192.168.3.4,,,,,,,ZB.AUTO,,

```


## Portmapper

## Порядок синхронизации



## Введение (в общем)
В мире многообразия систем, выполняющих различные задачи, часто возникает задача на основании данных 
одной или нескольких систем создать объекты (таблицы или сущности) в другой системе. 
В общем случае за это отвечает механизм `ETL`:

**ETL** (от англ. `Extract`, `Transform`, `Load` — дословно «извлечение, преобразование, загрузка»). 
Это системы корпоративного класса, которые применяются, чтобы привести к одним справочникам и загрузить в DWH (Data Warehouse, Хранилище данных) и EPM (Enterprise Performance Management, управление эффективностью бизнеса) данные из нескольких разных учетных систем.
Т.е. решает задачу однонаправленного обмена данными между исходной и целевой системой.

Подробнее можно почитать:
* [Wiki](https://ru.wikipedia.org/wiki/ETL)
* [Введение в ETL](https://bourabai.ru/tpoi/olap01-9.htm)
* [Habr. Основные функции ETL-систем](https://habr.com/post/248231/)


В общем виде процесс проходит по следующим этапам:
1. *Процесс извлечения* – его задача затянуть в ETL данные из внешней системы
2. *Процесс валидации данных* – на этом этапе данные последовательно проверяются на корректность и полноту
3. *Процесс привязки (mapping) данных* с целевой моделью – связывания данных с полями целевой модели
4. *Процесс агрегации данных* – 
5. *Загрузка в целевую систему* — это технический процесс использования коннектора и передачи данных в целевую систему.


## NOC

В НОКе реализован базовый функционал **ETL** - возможность извлекать данные из **внешней системы** [Remote System](../../../user/reference/concepts/remote-system/index.md) и на их основе получать объекты в НОКе. 
На данный момент возможна загрузка следующих сущностей:

* Зоны ответственности [Administrative Domain](../../../user/reference/concepts/administrative-domain/index.md)
* Объекты управления [Managed Object](../../../user/reference/concepts/managed-object/index.md)
* Профили объектов [Manged Object Profile](../../../user/reference/concepts/managed-object-profile/index.md)
* Сегменты [Segments](../../../user/reference/concepts/network-segment/index.md)
* Точки присутствия [PoP](../../../user/reference/concepts/container/index.md)
* Профили аутентификации (`Auth profile`)
* Сервисы [Services](../../../user/reference/concepts/service/index.md)
* Абоненты [Subscribers](../../../user/reference/concepts/subscriber/index.md)
* Линки (`Links`) - для построения связей по данным внешней системы [NRI](../../../admin/reference/discovery/box/nri.md)
* Ресурсные группы [Resource Group](../../../user/reference/concepts/resource-group/index.md)

Кратко механизм выглядит так:

1. Реализуется **адаптера выгрузки** (`extractor`). Его задача - получить данные из **внешней системы** и отдать в виде списка полей, определённых в `загрузчике`. Подробнее см главу `Загрузка`
2. В интерфейсе настраивается `Внешняя система` и выбираются реализованные `загрузчики`
3. После настройки даётся команда `./noc etl extract <remote_system_name>`. Происходит извлечение информации из внешней системе (при помощи адаптера, написанного на шаге 1). Всё складывается в файлы `import.csv.gz` в директории `/var/lib/noc/import/<remote_system_name>/<loader_name>/import.csv.gz`
4. Командой `./noc etl check <remote_system_name>` проверяем целостность выгрузки
5. Командой `./noc etl diff <remote_system_name>` смотрим изменения относительно предыдущего файла выгрузки. В первым раз все объекты будут показаны как новые.
6. Командой `./noc etl load <remote_system_name>` заливаем данные в НОК (при этом создаются объекты соотв. загрузчику). 

После окончания файл `import.csv.gz` перемещается в папку `/var/lib/noc/import/<remote_system_name>/<loader_name>/arcive/import_date.csv.gz` и файл `mappings.csv` дополняется связкой: `ID внешней системы` <-> `ID НОКа`. Также поля объектов `Remote System`, `Remote ID` - заполняются выгрузкой.


<!-- prettier-ignore -->
!!! info
    Путь `/var/lib/noc/import` задаётся настройкой `path` -> `etl_import`


### Настройка внешней системы

Настройка начинается в пункте меню `Main` -> `Setup` -> `Remote Systems`. После нажатия на кнопку `Add` открывается форма создания внешней ситемы с пунктами:
* `Name` - имя внешней системы. Будет использоваться при работе с командой `ETL`. Желательно выбирать краткое и без пробелов.
* `Description` - описание (какой-нибудь текст)
* `Handler` - ссылка на `адаптер загрузки` в виде строчки импорта питона. 
> Н-р: `noc.custom.etl.extractors.zabbix.ZBRemoteSystem` рассчитывает, что файлик лежит в кастоме по пути `<custom_folder>/etl/extractor/zabbix.py`
* `Extractors/Loaders` - список доступных для моделей для загрузки. Требует реализацию в адаптере.
* `Environment` - настройки адаптера загрузки (передаются в него при работе)

Также, в объектах, поддерживающих создание из механизма `ETL` присутствуют поля:

* `Remote System` - это указание из какой внешней системы приехал объект
* `Remote ID` - текстовое поле, ID объекта во внешней системе

<!-- prettier-ignore -->
!!! info
    Поля `Remote System`, `Remote ID` заполняются автоматически. Вносить изменения вручную не рекомендуется


После настройки внешней системы дальнейшая работа идёт с командой `./noc etl`. 
Для лучшего понимания мы начнём рассмотрение с последнего этапа - загрузки в НОК.


## Термины

* Внешняя система (`Remote System`) - Система, являющаяся источником данных для работы ETL
* `Extractor` - Адаптер загрузки, отвечающий за извлечение информации из `Внешней системы`, преобразование её к необходимому для работы формату
* `Loader` - адаптер загрузки. Создаёт сущности в НОКе и формирует файл привязки (`mapping file`)
* `mappings` формирует привязку между ID системам (ID НОКа <> ID внешней системы)
