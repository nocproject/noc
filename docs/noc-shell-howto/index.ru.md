# Использование консоли разработчика для настройки системы

Система представляет достаточно богатые возможности по расширению под задачи конкретного пользователя.
От разработки собственных адаптеров оборудования и API до изменения поведения системы путём
включения собственного кода [Обработчики] [Ссылка на документацию по Custom].

Разработка ведётся на *Языке программирования Python*.

## Консоль разработчика

В `Python` включена консоль разработчика (вызывается через `python`), в НОКе она расширена внутренними
модулями системы, что представляет удобный инструмент для разработки и тестирования расширения системы.

Для запуска консоли разработчика необходимо выполнить команду `./noc shell` из корневой НОКа.

!!! note
    Для удобства можно установить пакет `ipython` он расширит возможности консоли. Устанавливается командой `./bin pip install ipython`


После выполнения команды `./noc shell` вы окажетесь в консоли разработчика:

```shell
[root@test noc]# ./noc shell
Python 3.8.3 (default, Jun 18 2020, 20:51:40) 
Type 'copyright', 'credits' or 'license' for more information
IPython 8.5.0 -- An enhanced Interactive Python. Type '?' for help.

In [1]: 
```

Отобразится версия питона, версия `ipython`, если установлен. Для работы доступны все модули системы,
строка импорта начинается с префикса `noc.`, модули из [custom] - `noc.custom.`.
Например, для просмотра версии системы необходимо воспользоваться модулем `noc.core.version`:

```python
In [1]: from noc.core.version import version

In [2]: version.version
Out[2]: '22.2+noc-1968.169.c4875fdb'

```

При запуске консоли не происходит автоматического подключения к Базе данных системы.
Это удобно для локальной разработки профилей, но для работы с данными подключения требуется.
Выполнить его можно через модуль `noc.core.mongo.connection`:

```python
In [4]: from noc.core.mongo.connection import connect

In [5]: connect()
[noc.core.mongo.connection] Connecting to MongoDB {'db': 'test', 'username': 'test', 'password': '********', 'authentication_source': 'test', 'replicaSet': 'test', 'readPreference': 'secondaryPreferred', 'maxIdleTimeMS': 60000, 'host': 'mongodb://sova:********@192.168.1.100:27017/test'}

In [6]: 

```

При частом использовании прописывать подключение к базе может быть утомительным.
Для этих случаев `ipython` позволят задать скрипты для запуска. Это файлы `.py`, расположенные в папке
` ~/.ipython/profile_default/startup/`, которые выполняются при запуске системы. Пример файла `~/.ipython/profile_default/startup/00-mongo.py`:

```python
from noc.core.mongo.connection import connect
connect()


```

Необходимо отметить, что при работе через консоль разработчика не проверяются права доступа к записям
и по этой причине необходимо соблюдать осторожность при массовых обновлениях.

## Доступ к данным системы

Основной единицей описания данных в системе выступает модель (`Model`), в ней содержится:

* Место хранения и используемый фреймворк
* Описание полей данных
* Методы работы с данными

Модели расположены в подпапках `models` основных компонентов системы. Для *импорта модели* указывается путь к ней и название:

```python
In [2]: from noc.sa.models.managedobject import ManagedObject

```

!!! note
    Для работы с моделями требуется подключения к `Базе Данных` системы


Модель использует для работы один из двух фреймворков:
* `Django`, данных находятся в `PostgresSQL`
* `MongoEngine`, данные находятся в `MongoDB`

Перечень всех моделей системы можно найти в файле `models.py` в корне системы.
Для понимания на основе какого фреймворка реализована модель можно использовать функцию `is_document`:

```python
In [2]: from noc.sa.models.managedobject import ManagedObject
In [3]: from noc.models import is_document

In [4]: is_document(ManagedObject)
Out[4]: False

```

*API* работы с записями у фреймворков схожий, исключение составляется только вложенный документы (`EmbeddedDocument`) в моделях `MongoEngine`. 
Рассмотрим основные операции работы с записями:

* Выборка записей и применение фильтров. Для фильтрации по связанным полям необходимо указывать связанную запись.
  Подробнее доступные выражения для фильтрации можно подсмотреть в документации по `FrameWork`:

```python
In [2]: from noc.sa.models.managedobject import ManagedObject
In [8]: from noc.main.models.pool import Pool

In [11]: ManagedObject.objects.filter(name="21-166506")
Out[11]: <QuerySet [<ManagedObject: 21-166506>]>

In [12]: ManagedObject.objects.filter(name__contains="21-166506")
Out[12]: <QuerySet [<ManagedObject: 21-166506>, <ManagedObject: 21-166506#PE>]>

In [13]: Pool.objects.get(name="default")
Out[13]: <Pool: default>

In [14]: p = Pool.objects.get(name="default")
In [15]: ManagedObject.objects.filter(pool=p)
Out[15]: <QuerySet [<ManagedObject: 20-049475>, <ManagedObject: 21-043981>, <ManagedObject: 21-166201#PE>, <ManagedObject: 21-070948#PE>, <ManagedObject: 21-166506>,<ManagedObject: 20-458751#PE>, '...(remaining elements truncated)...']>

```

* Удаление записи. Производится методом `delete()`. При попытке удаления записи на которую есть ссылки будет исключение 
  `Referred from model` c указанием идентификатора модели и наименования записи.

```python
In [8]: from noc.main.models.pool import Pool

In [10]: p = Pool.objects.get(name="default")
In [14]: p.delete()

ValueError: Referred from model sa.ManagedObject: 20-049475 (id=24484)

```

* Добавление (создание) записи. Для добавления записи необходимо создать инстанс (`instance`) соответствующей модели,
   заполнить обязательные поля (*атрибут `is_required=True`*) и вызвать метод `save()`

```python
In [16]: p = Pool(name="default2")

In [17]: p.save()
Out[17]: <Pool: default2>

```


## Примеры

Рассмотрим несколько примеров как через консоль разработчиков можно проделывать рутинные операции.

### Создание, изменение и присвоение настройки

#### Вывод настроенные метрики для профиля объектов и профиля интерфейсов

Для хранения метрик используется вложенный документ, поэтому взаимодействие для *Профиля объекта* (`ManagedObject Profile`), использует `Django`, и
профиля интерфейса (`Interface Profile`), использует `MongoEngine`, будет отличаться. Начнём с *Профиля объекта*:

```python

# В данном случае нам понадобится по идентификатру метрики получить запись MetricType, и вывести её имя
# Также из вывода исключаются все Профили объекта с выключенным опросом метрик
In [30]: from noc.core.mongo.connection import connect
In [31]: from noc.sa.models.managedobjectprofile import ManagedObjectProfile
In [12]: from noc.pm.models.metrictype import MetricType
In [32]: connect()

In [29]: for mop in ManagedObjectProfile.objects.filter(enable_periodic_discovery_metrics=True, enable_periodic_discovery=True):
    ...:     print(f"Configured metrics for {mop.name}: ", ", ".join(MetricType.get_by_id(mc["metric_type"]).name for mc in mop.metrics))

```

Аналогично можно организовать проверку, что набор метрик настроен на *Профиле объекта* и распечатать если нет.

```python
In [30]: from noc.core.mongo.connection import connect
In [31]: from noc.sa.models.managedobjectprofile import ManagedObjectProfile
In [32]: from noc.pm.models.metrictype import MetricType
In [33]: connect()

In [34]: metrics_check = ["CPU | Usage", "Memory | Usage"]  # Задаём список имён метрик для проверки
In [35]: mt_check = {str(mt.id) for mt in MetricType.objects.filter(name__in=metrics_check)}  # Получаем записи с MetricType для работы

In [36]: for mop in ManagedObjectProfile.objects.filter(enable_periodic_discovery_metrics=True, enable_periodic_discovery=True):
    ...:     checks = set(mt_check)  # формируем множество для проверки (с ним быстрее)
    ...:     for mc in mop.metrics:
    ...:         if mc["metric_type"] in checks:
    ...:             checks.remove(mc["metric_type"])  # если метрика настроена - убираем её из множества
    ...:     if not checks:  #  Если все метрики присутствуют в настройках - переходим к следующему
    ...:         continue
    ...:     print(f"Not configured metrics on profile {mop.name}: ", ",".join(MetricType.get_by_id(c).name for c in checks))  # Используем метод get_by_id для получения инстанса MetricType по имени
```

То же самое для *Профиля интерфейса* будет выглядеть проще, поскольку реализовано через `EmbeddedDocument`


```python
In [30]: from noc.core.mongo.connection import connect
In [33]: from noc.inv.models.interfaceprofile import InterfaceProfile
In [34]: connect()

In [36]: for ip in InterfaceProfile.objects.filter(metrics__exists=True):
    ...:     print(ip.name, ", ".join(f"'{mc.metric_type.name}'" for mc in ip.metrics))  # В данном случае обращение mc.metric_type возвращает инстанс MetricType

```

Аналогично поиск не настроенных метрик

```python
In [30]: from noc.core.mongo.connection import connect
In [33]: from noc.inv.models.interfaceprofile import InterfaceProfile
In [34]: connect()

In [35]: metrics_check = ["CPU | Usage", "Memory | Usage"]  # Задаём список имён метрик для проверки
In [36]: for ip in InterfaceProfile.objects.filter(metrics__exists=True):
    ...:     checks= set(metrics_check)
    ...:     for mc in ip.metrics:
    ...:         if mc.metric_type.name in checks:  # Проверяем по имени
    ...:             checks.remove(mc.metric_type.name)
    ...:     if not checks:  #  Если все метрики присутствуют в настройках - переходим к следующему
    ...:         continue
    ...:     print(f"Not configured metrics on profile {ip.name}: ", ",".join(MetricType.get_by_name(c).name for c in checks))    # используем метод get_by_name длф для запроса инстанса MetricType по имени

```

#### Добавить метрику в настройки профиля согласно списка

В предыдущем пункте удалось реализовать проверку настроек.
Следующим шагом может быть внесение изменений в них. Для этого необходимо присвоить полю новое значение
и вызваить метод `save()`, который запишет измения в базу.

Рассмотрим пример добавления метрики в *Профиль объекта*

```python
In [30]: from noc.core.mongo.connection import connect
In [31]: from noc.sa.models.managedobjectprofile import ManagedObjectProfile, ModelMetricConfigItem
In [32]: from noc.pm.models.metrictype import MetricType
In [33]: connect()

In [36]: mop = ManagedObjectProfile.objects.get(name="default")  # Получаем инстанс Профиля объекта
In [37]: mop.metrics += [ModelMetricConfigItem(metric_type=str(MetricType.get_by_name('CPU | Usage').id), enable_periodic=True).dict()] # Добавляем метрику в список

In [38]: mop.save()  # Сохраняем изменение

```

Добавляем метрику в *Профиль интерфейса*

```python
In [30]: from noc.core.mongo.connection import connect
In [31]: from noc.inv.models.interfaceprofile import InterfaceProfile, InterfaceProfileMetrics
In [32]: from noc.pm.models.metrictype import MetricType
In [33]: connect()

In [36]: ip = InterfaceProfile.objects.get(name="default")  # Получаем инстанс Профиля интерфейса
In [37]: ip.metrics += [InterfaceProfileMetrics(metric_type=MetricType.get_by_name('Interface | Errors | In'), enable_periodic=True)]

In [38]: ip.save()
Out[60]: <InterfaceProfile: default>


```