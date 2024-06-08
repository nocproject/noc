# Написание собственных команд NOC

При необходимости постоянного использования кода его реализацию можно вынести в команду. Команды запускаются вызовом `./noc <command_name>`.

Пример команда для вывода версии - `./noc about` расположена в `commands/about.py`

```shell
[root@test noc]# ./noc about
22.2+noc-1968.161.9153a970
```

## Структура команды

В общем виде структура команды выглядит так:

``` python title="sample.py" linenums="1"
--8<-- "docs/writing-noc-command-howto/sample.py"
```

Рассмотрим пример детальнее:

``` python title="sample.py" linenums="1" hl_lines="1"
--8<-- "docs/writing-noc-command-howto/sample.py"
```

Импортируем базовый класс команды.

``` python title="sample.py" linenums="1" hl_lines="2"
--8<-- "docs/writing-noc-command-howto/sample.py"
```

Импортируем структуру, содержащую версию NOC

``` python title="sample.py" linenums="1" hl_lines="5"
--8<-- "docs/writing-noc-command-howto/sample.py"
```

Реализалия нашей команды должна находиться в классе `Command`,
порожденным от базового класса `BaseCommand`

``` python title="sample.py" linenums="1" hl_lines="6"
--8<-- "docs/writing-noc-command-howto/sample.py"
```

Точка входа в команду находится в функции `handle`, поэтому мы
должны ее переопределить.

``` python title="sample.py" linenums="1" hl_lines="7"
--8<-- "docs/writing-noc-command-howto/sample.py"
```

Функция `BaseCommand.print()` печатает аргумент на stdout, всегда
используйте ее, вместо встроенной функции `print()` в командах.
В данном случае мы печатаем версию.

``` python title="sample.py" linenums="1" hl_lines="10 11"
--8<-- "docs/writing-noc-command-howto/sample.py"
```

Эта часть кода является общей для всех команд и отвечает за
запуск нашей команды из командной строки.


## Пример c разбором аргументов

В качестве примера вынесем код проверки настроенных метрик в команду.
Добавим возможность передавать список метрик через параметры.
Расположим код в файле `commands/check-metrics.py`:

``` python title="check-metrics.py" linenums="1"
--8<-- "docs/writing-noc-command-howto/check-metrics.py"
```

Запустим на исполнение:

``` shell
[root@test noc]# ./noc check-metrics 'Interface | Errors | In'
Checking Interface Metric
Not configured metrics on profile Аплинк:  Interface | Errors | In
Not configured metrics on profile Порт РРЛ:  Interface | Errors | In
```

Рассмотрим пример детальнее:

``` python title="check-metrics.py" linenums="1" hl_lines="1 2 3"
--8<-- "docs/writing-noc-command-howto/check-metrics.py::13"
```

Импортируем стандартные модули python, которые понадобятся нам в дальнейшем.

``` python title="check-metrics.py" linenums="1" hl_lines="5 6 7 8 9 10"
--8<-- "docs/writing-noc-command-howto/check-metrics.py::13"
```

Нам также понадобятся импортировать несколько опеределений NOC.

``` python title="check-metrics.py" linenums="13" hl_lines="1"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:13:17"
```

Реализалия нашей команды должна находиться в классе `Command`,
порожденным от базового класса `BaseCommand`

``` python title="check-metrics.py" linenums="13" hl_lines="2"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:13:17"
```

Функция `add_arguments` позволяет настроить парсер команд `argsparse`
и настроить парсинг дополнительных аргументов.

``` python title="check-metrics.py" linenums="13" hl_lines="3"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:13:17"
```

Мы настраиваем парсер аргументов таким образом, чтобы весь остаток
командной строки (`REMAINDER`) был помещен в опцию `metrics`

``` python title="check-metrics.py" linenums="17" hl_lines="1"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:17:36"
```

Точка входа в команду находится в функции `handle`, поэтому мы
должны ее переопределить.

``` python title="check-metrics.py" linenums="17" hl_lines="2 3"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:17:36"
```
Мы проверяем, заданы ли парамеры командной строки (`option["metrics"]`),
если нет - вызываем функцию `BaseCommand.die()`. Функция `die()` печатает
сообщение об ошибке в stderr и завершает работу команды с системным кодом ошибки().

``` python title="check-metrics.py" linenums="17" hl_lines="4"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:17:36"
```
Функция `connect()` осуществляет соединение с базой mongodb. Она должна быть
выполнена заранее до любого обращения к базе.

``` python title="check-metrics.py" linenums="17" hl_lines="5"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:17:36"
```
Мы создаем два пустых списка:

* Метрики интерфейса: `interface_metrics`
* Метрики объекта: `object_metrics`

``` python title="check-metrics.py" linenums="17" hl_lines="6"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:17:36"
```
Мы пробегаем по всем параметрам командной строки (`option["metrics"]`), так как их может
быть больше одного.

``` python title="check-metrics.py" linenums="17" hl_lines="7"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:17:36"
```
Нам необходимо по имени метрики получить ее объект (запись в базе).
В NOC для получения записи по имени используются методы моделей `.get_by_name()`.
Помимо упрощения кода `.get_by_name()` также обеспечивает кеширование,
что может сильно повышать производительность.

``` python title="check-metrics.py" linenums="17" hl_lines="8 9 10"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:17:36"
```
Если запись не найдена, `.get_by_name()` возвращает `None`. Мы используем
проверку на `None`, чтобы убедиться, что пользователь правильно указал
имя метрики. Если пользователь указал неверное имя, мы печатаем сообщение
и переходим к обработке следующей метрики.

``` python title="check-metrics.py" linenums="17" hl_lines="11 12 13 14"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:17:36"
```
В этом месте мы проверяем, если metric scope - `Interface`, то добавляем
метрику в список `iface_metrics`, в противном случае - в `object_metrics`.

``` python title="check-metrics.py" linenums="17" hl_lines="15 16 17"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:17:36"
```
Если пользователь задал хоть одну объектную метрику, вызываем
функцию `check_object_metrics` и передаем ей в качестве параметра
список `object_metrics`

``` python title="check-metrics.py" linenums="17" hl_lines="18 19 20"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:17:36"
```
Если пользователь задал хоть одну интерфейсную метрику, вызываем
функцию `check_interface_metrics` и передаем ей в качестве параметра
список `interface_metrics`

``` python title="check-metrics.py" linenums="38" hl_lines="1"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:38:51"
```
Определим функцию `check_object_metrics`, которая принимает на вход
список объектных метрик.

``` python title="check-metrics.py" linenums="38" hl_lines="2"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:38:51"
```

Мы строим словарь `mt_check`, который в качестве ключа использует id метрики,
а в качестве значения хранит объект метрики.

``` python title="check-metrics.py" linenums="38" hl_lines="3 4 5"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:38:51"
```
Мы извлекаем все профили объекта, для которых включен periodic discovery
и заданы метрики.

``` python title="check-metrics.py" linenums="38" hl_lines="6"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:38:51"
```
Мы строим множество `check` по ключам `mt_check`. В дальнейшем мы будем убирать
из него найденные метрики.

``` python title="check-metrics.py" linenums="38" hl_lines="7 8 9"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:38:51"
```
Мы проходим по всем метрикам, заданным в профиле, и, если они присутствуют
в нашем `check`, удаляем их из множества `check`.

``` python title="check-metrics.py" linenums="38" hl_lines="10 11 12 13 14"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:38:51"
```

Если в нашем множестве `checks` остались мерики, пишем сообщение, что они
не сконфигурированы для профиля.

``` python title="check-metrics.py" linenums="53" hl_lines="1"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:53:62"
```
Определим функцию `check_interface_metrics`, которая принимает на вход
список интерфейсных метрик.

``` python title="check-metrics.py" linenums="54" hl_lines="2"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:53:62"
```
Мы проходим по всем профилям интерфейсов, для которых сконфигурированы метрики.

``` python title="check-metrics.py" linenums="54" hl_lines="3"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:53:62"
```
Мы строим множество `checks` из всех элементов входных параметров функции

``` python title="check-metrics.py" linenums="54" hl_lines="4 5 6"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:53:62"
```

Мы проходим по всем метрикам, заданным в профиле, и, если они присутствуют
в нашем `check`, удаляем их из множества `check`.

``` python title="check-metrics.py" linenums="54" hl_lines="7 8 9 10"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:53:62"
```

Если в нашем множестве `checks` остались мерики, пишем сообщение, что они
не сконфигурированы для профиля.

``` python title="check-metrics.py" linenums="65" hl_lines="1 2"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:65:66"
```

Эта часть кода является общей для всех команд и отвечает за
запуск нашей команды из командной строки.
