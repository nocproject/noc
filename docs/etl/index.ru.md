# ETL

Получение инвентарной информации из внешней системы позволяет автоматизировать добавление оборудования и настройку НОКа. 
Для этого в составе системы предусмотрена поддержка механизма `ETL` (Extract-Transfer-Load). Основная применяемая терминология:

* Внешняя система [Remote System](../concepts/remote-system/index.md) - источник данных для работы ETL
* `Extractor` - Адаптер *выгрузки*, модуль на `Python` отвечающий за извлечение информации из `Внешней системы`, преобразование её к необходимому для работы формату
* `Loader` - адаптер *загрузки*. Создаёт сущности в НОКе и формирует файл привязки (`mapping file`)
* `mappings` формирует привязку между ID системам (ID НОКа <> ID внешней системы)
* `DataModel` (Модель данных) - описание состава и структуры данных для работы загрузчика
* `Model` - модель данных НОКа, с которой работает загручзчик

Для взаимодействия с `ETL` предусмотрена команда `./noc etl`, при её запуске по базовому пути (`/var/lib/noc/import/`) 
создаётся структура папок в составе:

* `import.jsonl.gz` - файл с новой выгрузкой
* `archive` - папка с файлами предыдущих выгрузок
* `mappings.csv` - файл соответствия ID внешней системы <-> ID НОКа
* `import.csv.rej.gz` - файл с записями ошибок выгрузки (отсев)

```
/var/lib/noc/import/<RemoteSystemName>/
├── administrativedomain
│   ├── archive
│   ├── import.jsonl.gz
│   └── mappings.csv
├── container
│   ├── archive
│   ├── import.jsonl.gz
│   └── mappings.csv
├── link
│   └── archive
├── managedobject
│   ├── archive
|   │   ├── import-2021-04-13-23-17-08.jsonl.gz
|   │   ├── import-2021-09-05-16-26-45.jsonl.gz
|   │   └── import-2021-09-05-18-08-45.jsonl.gz
│   ├── import.csv.gz
│   ├── import.csv.rej.gz
│   ├── import.jsonl.gz
│   └── mappings.csv
├── managedobjectprofile
│   ├── archive
│   ├── import.jsonl.gz
│   └── mappings.csv
├── networksegment
│   ├── archive
│   ├── import.jsonl.gz
│   └── mappings.csv
├── networksegmentprofile
│   ├── archive
│   └── import.jsonl.gz
├── resourcegroup
│   ├── archive
│   └── mappings.csv
└── ttsystem
    ├── archive
    ├── import.jsonl.gz
    └── mappings.csv
```

<!-- prettier-ignore -->
!!! info

    Путь `/var/lib/noc/import` задаётся настройкой [path.etl_import](../config-reference/path.md#etl_import)

Кратко работа механизм выглядит следующим образом:

1. Реализуется **адаптер выгрузки** (`extractor`). Его задача - получить данные из **внешней системы** и отдать в виде списка полей, определённых в `загрузчике`. Подробнее см главу [Загрузка](#загрузчик-loader)
2. В интерфейсе настраивается [Внешняя система](../concepts/remote-system/index.md) и выбираются реализованные `загрузчики`
3. После настройки даётся команда `./noc etl extract <remote_system_name>`. Происходит извлечение информации из внешней системе (при помощи адаптера, написанного на шаге 1). Всё складывается в файлы `import.csv.gz` в директории `/var/lib/noc/import/<remote_system_name>/<loader_name>/import.csv.gz`
4. Командой `./noc etl check <remote_system_name>` проверяем целостность выгрузки
5. Командой `./noc etl diff <remote_system_name>` смотрим изменения относительно предыдущего файла выгрузки. В первым раз все объекты будут показаны как новые.
6. Командой `./noc etl load <remote_system_name>` заливаем данные в НОК (при этом создаются объекты соотв. загрузчику). 

После окончания файл `import.csv.gz` перемещается в папку `/var/lib/noc/import/<remote_system_name>/<loader_name>/archive/import_date.csv.gz` и файл `mappings.csv` дополняется связкой: `ID внешней системы` <-> `ID НОКа`. 
Также поля объектов `Remote System`, `Remote ID` - заполняются выгрузкой.

## Поддерживаемые модели

Для каждой из доступных сущностей системы описывается модель данных. В ней указывается поля и тип данных, доступные 
для выгрузки. Применяется библиотека [PyDantic](https://pydantic-docs.helpmanual.io). Модель расположены в папке `<noc_base>/core/etl/models`. 
Наследуются от базового класса `BaseModel`, для полей связи друг с другом используется тип `Reference`. Необязательные обозначаются как `Optional`:

``` python
class AdministrativeDomain(BaseModel):
    id: str
    name: str
    parent: Optional[Reference["AdministrativeDomain"]]
    default_pool: Optional[str]

    _csv_fields = ["id", "name", "parent", "default_pool"]
```

## Адаптер выгрузки

Процедура извлечение данных из внешней системы и сопоставление их с моделью называется выгрузка (`extract`). 
Для её работы необходим адаптер, в котором запрошенная информация транслируется в формат модели данных. 
В адаптере указывается класс внешней системы и классы получения данных (реализуют работу с отдельной моделью данных). Пример:

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
по пути: `<etl_path>/<remote_system_name>/<loader_name>/`

### Расчёт изменений и проверка целостности данных

Следующей после выгрузки запускается контроль целостности данных. Проверяются ссылки на данные полученные для других моделей 
поля типа `Reference`. Проверка запускается командой `./noc etl check <REMOTE_SYSTEM_NAME>`, в случае проблем выводится сообщение:
```
[noc.core.etl.loader.base] [RS|managedobject] ERROR: Field #4(administrative_domain) == 'administrativedomain' refers to non-existent record: 10106,mos-pma-pta-pta1-sw01#10106,True,,administrativedomain,default,!new,Generic.Host,zb.std.sw,,,2,192.168.3.2,,,,,,,ZB.AUTO,,
[noc.core.etl.loader.base] [RS|managedobject] ERROR: Field #4(administrative_domain) == 'administrativedomain' refers to non-existent record: 10107,mos-pma-lta-lta1-sw01#10107,True,,administrativedomain,default,!new,Generic.Host,zb.std.sw,,,2,192.168.3.4,,,,,,,ZB.AUTO,,
```

В нём указывается название поля (`administrative_domain`), модель, на которую оно ссылается и запись с ошибкой.

Посмотр изменений доступен по команде `./noc etl diff <REMOTE_SYSTEM_NAME> <ExtractorNAME>`. В выводе 
отображается разница между новой и текущей (последний успешной) выгрузками. Изменённые записи показываются построчно с указателем:

* `/` - изменение записи
* `+` - новая запись (будет добавлена в систему)
* `-` - отсутствие записи (будет удалена из системы)

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

## Загрузчик (Loader)

Последним этапом является загрузка изменений в НОК. Загрузчики для моделей находятся в папке `core/etl/loader`, 
в ней располагаются файлы с классами загрузчиков. Например, в загрузчике для `ManagedObject` определёны следующие аттрибуты:

* `name` - имя загрузчика
* `model` - ссылка на реализуемую модель системы
* `data_model` - ссылка на модель данных 
* метод `purge` - позволяет переопределять поведение системы при удалении. В примере вместо удаления устройства из системы 
оно переводится в неуправляемые и очищается ссылка на контейнер

```python

class ManagedObjectLoader(BaseLoader):
    """
    Managed Object loader
    """

    name = "managedobject"
    model = ManagedObjectModel
    data_model = ManagedObject

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clean_map["pool"] = Pool.get_by_name
        self.clean_map["fm_pool"] = lambda x: Pool.get_by_name(x) if x else None
        self.clean_map["profile"] = Profile.get_by_name
        self.clean_map["static_service_groups"] = lambda x: [
            str(x.id) for x in ResourceGroup.objects.filter(remote_id__in=x)
        ]
        self.clean_map["static_client_groups"] = lambda x: [
            str(x.id) for x in ResourceGroup.objects.filter(remote_id__in=x)
        ]

    def purge(self):
        """
        Perform pending deletes
        """
        for r_id, msg in reversed(self.pending_deletes):
            self.logger.debug("Deactivating: %s", msg)
            self.c_delete += 1
            try:
                obj = self.model.objects.get(pk=self.mappings[r_id])
                obj.is_managed = False
                obj.container = None
                obj.save()
            except self.model.DoesNotExist:
                pass  # Already deleted
        self.pending_deletes = []

```


**Загрузка** заливка извлечённых данных в НОК выполняется командой `./noc etl load <REMOTE_SYSTEM_NAME>`. Процедура выглядит следующим образом:

1. Добавление и изменение записей происходит в порядке их появления
2. Удаления записей происходит в конце (после изменений и удалений)
3. Файл привязки идентификаторов внешней системы и локальных обновляется в конце выгрузки
4. Удаление происходит согласно методу `purge` загрузчика

<!-- prettier-ignore -->
!!! warning

    Важно понимать, что изменения вычисляются относительно предыдущей загрузки (предыдущего состояния) из внешней системы. По этой причине, если внести изменения по полю в НОКе - загрузка эти изменения не откатит. Также, если потерять архивные файлы по последней выгузке, то все объекты будут пересозданы.


## Portmapper

Специальный адаптер, в котором описываются правила привязки портов во внешней системе к интерфейсам `ManagedObject` в НОК. 
Используется в линковке по данным внешней системы [portmapper](../discovery-reference/box/nri.md)
