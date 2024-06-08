# Handler Reference

**Handlers** are used to extend the system's functionality by implementing custom functions. They are Python modules with implemented functions. In the system, they are represented as function pointers, such as `noc.main.handlers.default_handlers.empty_handler`. The actual functions are registered in the system using the import string as a pointer to the function. For example, there is a default handler in the system located at `main/handlers/default.py`. When called, it prints the passed arguments.

## List of Available Handlers

| Name                                        | Interface                  | Trigger                                                 | Settings                                                              |
| ------------------------------------------- | -------------------------- | ------------------------------------------------------- | --------------------------------------------------------------------- |
| [Config Filter](config-filter.md)           | `Allow Config Filter`      | [Config](../discovery-reference/box/config.md) scan     | [Managed Object](../concepts/managed-object/index.md)                 |
| [Config Diff Filter](config-diff-filter.md) | `Allow Config Diff Filter` | [Config](../discovery-reference/box/config.md) scan     | [Managed Object](../concepts/managed-object/index.md)                 |
| [Config Validation](config-validation.md)   | `Allow Config Validation`  | [Config](../discovery-reference/box/config.md) scan     | [Managed Object](../concepts/managed-object/index.md)                 |
| [Address Resolver](address-resolver.md)     | `Allow Address Resolver`   | [Discovery](../discovery-reference/box/hk.md) scan      | [Managed Object Profile](../concepts/managed-object-profile/index.md) |
| [Housekeeper](housekeeper.md)               | `Allow Housekeeping`       | [HK](../discovery-reference/box/hk.md) scan             | [Managed Object Profile](../concepts/managed-object-profile/index.md) |
| [DS Filter](ds-filter.md)                   | `Allow DS Filter`          | [Datastream](../datastream-api-reference/index.md) scan | [DS Filter](../concepts/managed-object-profile/index.md)              |
| [Iface Description](ifacedescription.md)    | `Allow Iface Description`  | [ifDesc](../discovery-reference/box/ifdesc.md) scan     | [Managed Object Profile](../concepts/managed-object-profile/index.md) |

## Examples

You can check a handler through `./noc shell`:

```python

from noc.core.mongo.connection import connect
from noc.core.handler import get_handler

connect()
h = get_handler(<handler_path>)
h()
```

## Dumping Variables

This handler prints the provided arguments.

```python
    def empty_handler(*args, **kwargs):
        print("[empty_handler] Arguments", args, kwargs)
```
