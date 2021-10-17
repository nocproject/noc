# Scripts


Инициализация профиля осуществляется в файле ``__init.py__``. В нём, путём наследования класса :py:class:`noc.core.profile.base.BaseProfile` происходит переопределение настроек работы с оборудованием по умолчанию. Также в него выносятся методы, которые используются в нескольких скриптах.

Реализация интерфейсов и работы с оборудованием осуществляется в файлах скриптов. В них, путём наследования класса :py:class:`noc.core.script.base.BaseScript` реализуется логика работы с оборудованием и нормализация полученных данных для передачи в NOC.
Базовый набор скриптов для взаимодействия с оборудованием состоит из:

* get_version Реализует интерфейс :py:class:`noc.sa.interfaces.igetversion.IGetVersion` . Запрашивает с оборудования платформу, версию ПО, и дополнительные аттрибуты (например, имя файла образа ПО, серийный номер...)
* get_capabilities Реализует интерфейс :py:class:`noc.sa.interfaces.igetcapabilities.IGetCapabilities` . Производит опрос оборудования на предмет поддерживаемых протоколов (SNMP, LLDP, CDP). Данная информация используется при вызове скриптов и внутри, для принятия решения, по какому протоколу работать.
* get_interfaces Рализует интерфейс :py:class:`noc.sa.interfaces.igetinterfaces.IGetInterfaces` . Запрашивает список интерфейсов с оборудования.

Для построения :term:топологии потребуются скрипты:

* get_chassis_id (реализует интерфейс :py:class:`IGetChassisid` ). 
* get_fqdn (реализует интерфейс :py:class:`IGetFqdn` )
* get_<method>_neighnbors (реализует интерфейс соответствующего метода)
    * get_cdp_neighbors (реализует интерфейс :py:class:`IGetCDPNeighbors` )
    * get_lldp_neighbors (реализует интерфейс :py:class:`IGetLLDPNeighbors` )
    * get_udld_neighbors (реализует интерфейс :py:class:`IGetUDLDNeighbors` )
* get_mac_address_table (реализует интерфейс :py:class:`IGetConfig` )
* get_arp (реализует интерфейс :py:class:`IGetArp` )

Для сбора конфигурации

* get_config (реализует интерфейс igetconfig)

Для сбора состава оборудования

* get_inventory (реализует интерфейс igetinventory)

По необходимости, в профиле может быть добавлено любое количество файлов скриптов.

.. _rst_device_interaction_label:

## Взаимодействие с оборудованием

Для взаимодействия с оборудованием базовый класс `noc.core.script.base.BaseScript` предоставляет следующие методы.

### CLI


.. automethod:: noc.core.script.base.BaseScript.cli


Метод позволяет выполнять команды на оборудовании. Возвращает вывод запрошенной команды в виде строки с текстом к которой, в дальнейшем, возможно применять любые методы для работы с текстовыми строками в Python.

.. ps Полный перечень доступных методов смотрите в приложении.

### SNMP


.. automethod:: noc.core.script.snmp.base.SNMP.get

.. automethod:: noc.core.script.snmp.base.SNMP.getnext

Методы позволяют выполнять SNMP запросы к оборудованию путём вызова метода с передачей ему OID'а. Для облегчения работы по SNMP, можно использовать:

.. automethod:: noc.core.script.snmp.base.SNMP.get_table

.. automethod:: noc.core.script.snmp.base.SNMP.get_tables

Полный перечень доступных методов смотрите в приложении.

### HTTP


.. automethod:: noc.core.script.http.base.HTTP.get

.. automethod:: noc.core.script.http.base.HTTP.post

Выполняет, соответственно, GET и POST запрос к оборудованию. В рельзультате возвращает ответ в виде JSON.



.. code-block:: python

    def execute(self):
        v = ""

И, в методе `execute()` идёт обращение к методам работы с оборудованием, получение информации и, в конце, результат передаётся через оператор `return`.

.. literalinclude:: ../examples/get_version.py
    :language: python
    :lines: 7-18, 57-81, 90-
    :linenos:


Скрипт ``get_capabilities`` отличается от остальных скриптов. Его предназначение - определять поддержку оборудованием того или иного функционала. В дальнейшем подобная информация используется для оптимизации опроса оборудования. Например, если оборудование не поддерживает SNMP (например он отключён, или в настройках указан наверный SNMP Community) то скрипты, которые требуют рабочего SNMP не выполняются. Также отличием является то, что он относится к категории *модульных* скриптов. И он наследует не класс :py:class:`noc.core.script.base.BaseScript` а класс вышестоящего скрипта ``noc.sa.profiles.Generic.get_capabilities``. Также, в нём используется специальная конструкция - :term:`декоратор` .Это позволяет обрабатывать ошибки, при вводе комманд, как стандартную ситуацию и делать вывод о недоступности функционала.

Рассмотрим пример. В стройках 2, 3 мы импортируем модули. В отличие от остальных скриптом, импортируются ``noc.sa.profiles.Generic.get_capabilities`` и ``noc.sa.profiles.Generic.get_capabilities``. Строки с интерфейсом нет, т.к. она определена в вышестоящем скрипте - ``Generic.get_capabilities``. По этой же причине отсутствует метод ``exetcute()``, он вызывается из вышестоящего скрипта.

.. literalinclude:: ../examples/get_capabilities.py
    :language: python
    :lines: 9-32
    :linenos:

Полный перечень проверяемых возможностей можно посмотреть в скрипте ``Generic.get_capabilities``

::: noc.sa.profiles.Generic.get_capabilities.Script
    rendering:
      show_source: true

После отработки скрипта get_capabilities становится возможно пользоваться данными проверок. Для этого используются методы :py:meth:`BaseScript.has_capability` , :py:meth:`BaseScript.has_snmp` .

Все особенности работы с тем или иным оборудованием сосредоточены внутри профиля. Чем больше информации сможет собрать профиль (в рамках потребляемого NOC'ом), тем больше будет знать NOC.

.. note:: Происходящее внутри профиля, целиком возложена на разработчика. И после запуска NOC'ом не контролируется.


### Примеры скриптов


* Huawei.VRP.get_version 

.. literalinclude:: ../examples/get_version.py
                            :language: python

* Huawei.VRP.get_capabilities

.. literalinclude:: ../examples/get_capabilities.py
                            :language: python


.. _rst-application-label:

## Приложение


.. _rst-base-class-profile-label:

### Базовый класс скрипта

.. automodule:: noc.core.script.base
    :members:
    :undoc-members:
    :show-inheritance:

.. _rst-interfaces-label:

### Интерфейсы NOCа


Профиль передаёт данные в сторону основной системы через интерфейс обмена данными. Интерфейс описывает формат и набор данных, который должен вернуть скрипт его реализующий. Существуют следующие интерфейсы для реализации профилем:

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
