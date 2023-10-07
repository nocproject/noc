# Config Filter Handler

Интерфейс для фильтра конфигурации оборудования. Фильтр конфигурации применяется
перед тем, как конфигурации сохранится в базу (`GridVCS`).
Служит для изменения конфигурации в процессе обработки, на вход подаётся собранная конфигурация.
Допустимы любые манипуляции, включая удаление частей и перезапись всего текста.

Фильтр конфигурации применяется перед [Config Diff Filter](config-diff-filter.md).

 
    config_filter(managed_object, config):
        Implements config filter
    
        :param managed_object: Managed Object instance
        :param config: Config (string)
        :returns: altered config (string)

## Примеры

### Удаление пароля

Заменяет *password <mypass>* на *password xxx*

```python
    import re

    rx_password = re.compile("password\s+(\S+)")

    def config_filter(mo, config):
        return rx_password.sub("xxx", rx_password)
```