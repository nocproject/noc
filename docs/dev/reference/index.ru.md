# Handler Overview

**Обработчики** (`Handlers`) используются для расширения функционала системы путём реализации пользовательских функций. 
Представляет собой модуль на `python` с реализованными функциями. В системе представлен в виде указателя на функцию - `noc.main.handlers.default_handlers.empty_handler`
Сами функции регистрируются в меню Он регистрируется в системе, использую строку импорта в качестве указателя на функцию. Например, в системе есть обработчик по умолчанию расположен в `main/hadlers/default.py`. При вызове он распечатывает переданные аргументы. 

## Перечень доступных обработчиков

| Имя  | Интерфейс    | Запуск                                                           | Настройки     |
| ---- | --- |------------------------------------------------------------------| ---- | 
| [Config Filter](config-filter.md) | `Allow Config Filter` | Опрос [Config](../../admin/reference/discovery/box/config.md) | [Managed Object](../../user/reference/concepts/managed-object/index.md) |
| [Config Diff Filter](config-diff-filter.md) | `Allow Config Diff Filter` | Опрос [Config](../../admin/reference/discovery/box/config.md) | [Managed Object](../../user/reference/concepts/managed-object/index.md) |
| [Config Validation](config-validation.md) | `Allow Config Validation` | Опрос [Config](../../admin/reference/discovery/box/config.md) | [Managed Object](../../user/reference/concepts/managed-object/index.md) |
| [Address Resolver](address-resolver.md) | `Allow Address Resolver` | Опрос [Discovery](../../admin/reference/discovery/box/hk.md)  | [Managed Object Profile](../../user/reference/concepts/managed-object-profile/index.md) | 
| [Housekeeper](housekeeper.md) | `Allow Housekeeping` | Опрос [HK](../../admin/reference/discovery/box/hk.md)         | [Managed Object Profile](../../user/reference/concepts/managed-object-profile/index.md) |
| [DS Filter](ds-filter.md) | `Allow DS Filter` | [Datastream](../api/datastream/index.md)                         | [DS Filter](../../user/reference/concepts/managed-object-profile/index.md) |
| [Iface Description](ifacedescription.md) | `Allow Iface Description` | Опрос [ifDesc](../../admin/reference/discovery/box/ifdesc.md) | [Managed Object Profile](../../user/reference/concepts/managed-object-profile/index.md) |

## Примеры

Проверить обработчик можно через `./noc shell`:

```python

from noc.core.mongo.connection import connect
from noc.core.handler import get_handler

connect()
h = get_handler(<handler_point>)
h()
```

### Распечатка переменных

Обработчик распечатывает переданные аргументы

```python
    def empty_handler(*args, **kwargs):
        print("[empty_handler] Arguments", args, kwargs)
```
