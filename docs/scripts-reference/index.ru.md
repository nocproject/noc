# Scripts Reference

Реализация интерфейсов и работы с оборудованием осуществляется в файлах скриптов. 
В них, путём наследования класса :py:class:`noc.core.script.base.BaseScript` реализуется логика работы с оборудованием и нормализация полученных данных для передачи в NOC.

## Список скриптов

| Название скрипта                                        | Интерфейс                | Generic   | Назначение                                               |
| ------------------------------------------------------- | ------------------------ | --------- | -------------------------------------------------------- |
| [get_version](get_version.md)                           | `IGetVersion`            | {{ no }}  | Сбор версии и платформы устройства                       |
| [get_capabiliries](get_capabilities.md)                 | `IGetCapabilities`       | {{ yes }} | Сбор поддержки оборудованием функционала (протоколонов ) |
| [get_config](get_config.md)                             | `IGetConfig`             | {{ no }}  | Сбор конфигурации                                        |
| [get_interfaces](get_interfaces.md)                     | `IGetInterfaces`         | {{ yes }} | Запрашивает список интерфейсов с оборудования.           |
| [get_inventory](get_inventory.md)                       | `IGetInventory`          | {{ yes }} | Для сбора состава оборудования                           |
| [get_chassis_id](get_chassis_id.md)                     | `IGetChassisid`          | {{ yes }} | Заправшивает `MAC` адрес устройства (шасси)              |
| [get_fqdn](get_fqdn.md)                                 | `IGetFqdn`               | {{ yes }} | Запрашивает `hostname` устройства                        |
| [get_mac_address_table](get_mac_address_table.md)       | `IGetMACAddressTable`    | {{ yes }} | Собирает таблицу `MAC` адресов устройства                |
| [get_arp](get_arp.md)                                   | `IGetArp`                | {{ yes }} | Собирает таблицу `ARP` устройства                        |
| [get_cdp_neighbors](get_cdp_neighbors.md)               | `IGetCDPNeighbors`       | {{ yes }} | Заправшивает таблицу соседей протокола CDP               |
| [get_fdp_neighbors](get_fdp_neighbors.md)               | `IGetFDPNeighbors`       | {{ yes }} | Заправшивает таблицу соседей протокола FDP               |
| [get_huawei_ndp_neighbors](get_huawei_ndp_neighbors.md) | `IGetHuaweiNDPNeighbors` | {{ yes }} | Заправшивает таблицу соседей протокола Huawei NDP        |
| [get_lacp_neighbors](get_lacp_neighbors.md)             | `IGetLACPNeighbors`      | {{ yes }} | Заправшивает таблицу соседей протокола LACP              |
| [get_lldp_neighbors](get_lldp_neighbors.md)             | `IGetLLDPNeighbors`      | {{ yes }} | Заправшивает таблицу соседей протокола LLDP              |
| [get_udld_neighbors](get_udld_neighbors.md)             | `IGetUDLDNeighbors`      | {{ yes }} | Заправшивает таблицу соседей протокола UDLD              |

## Структура скрипта

Пример файла скрипта:

```python
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re


class Script(BaseScript):
    name = "Huawei.VRP.get_version"
    cache = True
    interface = IGetVersion

    def execute_cli(self, **kwargs):
        v = self.cli("display version")
        ...

    def execute_snmp(self, **kwargs):
        v = self.snmp.get("1.XXXX")
        ...

```

Структура файла скрипта следующая

1. **Область импорта**. В ней, мы импортируем базовый класс (строка 1) скрипта и интерфейс, реализуемый скриптом (строка 2). Здесь же можно импортировать необходимые для работы скрипта модули. Например, модуль поддержки регулярных выражений (строка 3)
2. После импорта необходимых модулей мы объявляем класс `Script`, наследую его от базового класса (`BaseScript`). После указываем полное имя скрипта, интерфейс и есть ли необходимость кэшировать результат выполнения.
3. **cache** - выставленный в `True` кэширует результат выполнения скрипта. При вызове из других скриптов через `self.scripts.<script_name>()`  
4. Методы работы с оборудованием - `execute_snmp()` и `execute_cli()` очерёдность выполнения задаётся приоритетом. Приоритет можно задать в настройках [ManagedObject](../concepts/managed-object/index.md)
5. При наличии метода `execute()` исполнение всегда начинается с него, даже при наличии `execute_snmp()` или `execute_cli()` это можно использовать для вмешательство в определении приоритета выволнения 


## Взаимодействия с оборудованием

В базовом классе реализованы методы работы с оборудованием:



Для взаимодействия с оборудованием базовый класс `noc.core.script.base.BaseScript` 

### CLI

Текстовый интерфейс работы с оборудование. Реализуется через `Telnet` или `SSH`. За работу отвечает метод `BaseScript.cli`, 
позволяет выполнять команды на оборудовании. Команда передаётся в виде текстового аргумента, возвращается вывод запрошенной команды в виде строки с текстом. 
Дальнейшая работа остаётся на совести разработчика.

.. automethod:: noc.core.script.base.BaseScript.cli


В случае ошибки выполнения команды может поднять исключение (`Exception`):
* `CLISyntaxError` - ошибка команды. Определяется на основе настройки `pattern_syntax_error`
* `CLIOperationError` - ошибка команды. Определяется на основе настройки  `pattern_operation_error`

Их можно перехватывать и использовать для изменения поведения скрипта.

### SNMP

Методы позволяют выполнять SNMP запросы к оборудованию, в качестве аргумента передаётся `OID`. 
Результат возвращается в виде числа или строки. 


::: noc.core.script.snmp.base:SNMP.get
    selection:
        docstring_style: restructured-text
    rendering:
        show_root_heading: true
        heading_level: 4
        show_category_heading: true

::: noc.core.script.snmp.base:SNMP.getnext
    selection:
        docstring_style: restructured-text
    rendering:
        show_root_heading: true
        heading_level: 4
        show_category_heading: true

Для облегчения работы по SNMP, можно использовать `mib`

::: noc.core.script.snmp.base:SNMP.get_table
    selection:
        docstring_style: restructured-text
    rendering:
        show_root_heading: true
        heading_level: 4
        show_category_heading: true

::: noc.core.script.snmp.base:SNMP.get_tables
    selection:
        docstring_style: restructured-text
    rendering:
        show_root_heading: true
        heading_level: 4
        show_category_heading: true

Для облегчения работы с `SNMP` есть встроенный модуль - `mib`, он позволяет конвертировать текстовые имена в соответствующий `OID`. 
Для этого имя должно присутствовать в базе `cmibs` (находятся в `<base_noc>/cmibs`). Подробнее как добавить `MIB` в `cmibs`.:

```python
from noc.core.mib import mib

mib["BRIDGE-MIB::dot1dBasePortIfIndex"]
: '1.3.6.1.2.1.17.1.4.1.2'
mib["BRIDGE-MIB::dot1dBasePortIfIndex", 100]
: '1.3.6.1.2.1.17.1.4.1.2.100'

```

Достаточное большое число данных в `SNMP` передаётся в `OctetString`, для их правильной интерпретации необходимо наличие `MIB` с заполненными `DISPLAY_HINTS`. 
Но возможно самостоятельно задать функцию для преобразования через аругмент `display_hints`. Встроенные функции расположены в модуле `noc.core.snmp.render`:

```python
from noc.core.script.base import BaseScript
from noc.core.mib import mib
from noc.core.snmp.render import render_bin

class Script(BaseScript):

    ...

    def execute_snmp(self, **kwargs):
        ...
        
        for oid, ports_mask in self.snmp.getnext(
            mib["Q-BRIDGE-MIB::dot1qVlanCurrentEgressPorts"],
            display_hints={mib["Q-BRIDGE-MIB::dot1qVlanCurrentEgressPorts"]: render_bin},
        ):
           ...
```

### HTTP

Выполняет, соответственно, GET и POST запрос к оборудованию. В качестве аргумента передаётся `URL`, 
в результате возвращается ответ при ошибке поднимается исключение `HTTPError` (`noc.core.script.http.base.HTTPError`)

::: noc.core.script.http.base:HTTP.get
    selection:
        docstring_style: restructured-text
    rendering:
        show_root_heading: true
        heading_level: 4
        show_category_heading: true

::: noc.core.script.http.base:HTTP.post
    selection:
        docstring_style: restructured-text
    rendering:
        show_root_heading: true
        heading_level: 4
        show_category_heading: true

При выполнении запроса есть возможность использовать схему аутентифиации - `Basic`, 
для этого параметр `use_basic` выставляется в `True`. Более сложные схемы реализуюся через механизм `Middleware`. 
Это промежуточный обработчик, которому передаётся запрос перед отправкой что позволяет модифицировать его данные или заголовок. 
Встроенные обработчики находятся в модуле `noc.core.script.http.middleware.*`, для их применения достаточно указать имя в настройке `http_request_middleware`. 
Для работы его работы  `Middleware` в [профиле SA](../concepts/sa-profile/index.md) доступны настройки:

* `enable_http_session` - авторизовать один раз за сессию
* `http_request_middleware` - список `Middleware`

Например, для `Digest` аутентификации в `profile.py` добавляются `digestauth`:

```python

    enable_http_session = True
    http_request_middleware = [
        "digestauth",
    ]
```

При необходимости можно добавлять обработчики для профиля. Они наследуются от класса `BaseMiddleware` и помещаются в папку 
`<profile>/middleware/`. Для работы в `http_request_middleware` добавляется строка импорта - 
`noc.sa.profiles.<profile_name>.middleware.<module_name>.<class_name>`.
 
Пример:

```python

# Python modules
import orjson
import hashlib
import codecs

# NOC modules
from noc.core.script.http.middleware.base import BaseMiddleware
from noc.core.http.client import fetch_sync
from noc.core.comp import smart_bytes


class AuthMiddeware(BaseMiddleware):
    """
    Append HTTP Digest authorisation headers
    """

    name = "customauth"

```


### MML

Протокол для машинного обмена данными [MML](https://en.wikipedia.org/wiki/MML_(programming_language), 
применяется в различных системах телефонии (АТС).  


### RTSP

Протокол управления стримингом потоков [Real Time Streaming Protocol](https://en.wikipedia.org/wiki/Real_Time_Streaming_Protocol). 
Применяется в различных системах видеонаблюдения (камерах, видеорегистраторах) для управления потоком видео. 
Также позволяет запрашивать информацию о доступных потоках. 
Например, получение состояния порта RTSP выглядит следующим образом:

```python
from noc.core.script.base import BaseScript
from noc.core.script.rtsp.error import RTSPConnectionRefused, RTSPAuthFailed


class Script(BaseScript):

    ...

    def execute(self, **kwargs):
        ...
        
        try:
            check = self.rtsp("DESCRIBE", "/Streaming/Channels/101/")
        except RTSPConnectionRefused:
            check = 0
```


## Generic Scripts

Часть скриптов уже реализовано в общем виде (через `SNMP`). Они доступны в профиле `Generic` - `<noc_base>/sa/profiles/Generic`. 
Функционал скриптов из `generic` можно использовать наследуюя их переопределяя функицонал через аттрибуты. 
Например, если оборудование поддерживает `SNMP`, то для реализация скрипта `get_interfaces` можно воспользоваться наследованием:

```python
# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "<profile_name>.get_interfaces"
    interface = IGetInterfaces

```

В этом случае будет достаточно фунционала базового скрипта.


## Кастомизация 


### Примеры скриптов


self.profile

* Huawei.VRP.get_version 

.. literalinclude:: ../examples/get_version.py
                            :language: python

* Huawei.VRP.get_capabilities

.. literalinclude:: ../examples/get_capabilities.py
                            :language: python


.. _rst-application-label:


### Базовый класс скрипта


::: noc.core.script.base:BaseScript
    selection:
        docstring_style: restructured-text
        members: true
        filters:
          - "!_x_seq"
          - "!__call__"
          - "!__init__"
          - "!apply_matchers"
          - "!clean_input"
          - "!clean_output"
          - "!run"
          - "!compile_match_filter"
          - "!match"
          - "!call_method"
          - "!root"
          - "!get_cache"
          - "!set_cache"
          - "!schedule_to_save"
          - "!push_prompt_pattern"
          - "!pop_prompt_pattern"
          - "!get_timeout"
          - "!get_cli_stream"
          - "!close_cli_stream"
          - "!close_snmp"
          - "!get_mml_stream"
          - "!close_mml_stream"
          - "!get_rtsp_stream"
          - "!close_rtsp_stream"
          - "!close_current_session"
          - "!close_session"
          - "!get_access_preference"
          - "!get_always_preferred"
          - "!to_reuse_cli_session"
          - "!to_keep_cli_session"
          - "!push_cli_tracking"
          - "!push_snmp_tracking"
          - "!iter_cli_fsm_tracking"
          - "!request_beef"
    rendering:
        heading_level: 4
        show_source: false
        show_category_heading: true
        show_root_toc_entry: false
        show_if_no_docstring: true

.. automodule:: noc.core.script.base
    :members:
    :undoc-members:
    :show-inheritance:

.. _rst-interfaces-label:


### Интерфейсы NOCа


Профиль передаёт данные в сторону основной системы через интерфейс обмена данными. Интерфейс описывает формат и набор данных, который должен вернуть скрипт его реализующий. Существуют следующие интерфейсы для реализации профилем:

::: noc.sa.interfaces.igetversion:IGetVersion
    rendering:
      show_source: true

::: noc.sa.interfaces.igetinterfaces:IGetInterfaces
    selection:
      docstring_style: restructured-text
    rendering:
      show_source: true

.. automodule:: noc.sa.interfaces.igetversion
    :members:
    
.. automodule:: noc.sa.interfaces.igetcapabilities
    :members:

.. automodule:: noc.sa.interfaces.igetinterfaces
    :members:
    :show-inheritance:

.. automodule:: noc.sa.interfaces.igetchassisid
    :members:

.. automodule:: noc.sa.interfaces.igetfqdn
    :members:

.. automodule:: noc.sa.interfaces.igetlldpneighbors
    :members:

.. automodule:: noc.sa.interfaces.igetcdpneighbors
    
    .. autoclass:: IGetCDPNeighbors
    
.. automodule:: noc.sa.interfaces.igetarp
    :members:

.. automodule:: noc.sa.interfaces.igetmacaddresstable
    :members:

.. automodule:: noc.sa.interfaces.igetconfig
    :members:

.. automodule:: noc.sa.interfaces.igetinventory
    :members:

.. _rst-interface-data-type-label:

### Типы данных, применяемые в интерфейсах NOC'а


В интерфейсах применяются следующие типы данных:

.. automodule:: noc.sa.interfaces.base
    :members:
