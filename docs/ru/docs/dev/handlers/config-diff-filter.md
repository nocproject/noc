# Config Diff Filter Handler


Интерфейс для фильтрации конфигурации для сравнения. 
Обработчик применяется для последней (собранной с оборудования) и текущей (последней сохранённой в базе) конфигурациям. 
Позволяет убрать из конфигурации постоянно меняющиеся части, не влияющие на расчёт разницу. 
Результат работы `Config Diff Filter` используется только для обнаружения разницы и не сохраняется в базе.

Config Diff Filter применяется после [Config Filter](config-filter.md).

    config_diff_filter(managed_object, config):
        Implements config diff filter
    
        :param managed_object: Managed Object instance
        :param config: Config (str)
        :returns: altered config (str)

## Примеры

### Скрыть сохранённое время

Удалить *ntp date XXX*

```python

    import re

    rx_ntp = re.compile("^ntp\s+date\s+\d+$", re.MULTILINE)

    def config_diff_filter(mo, config):
        return rx_ntp.sub("", rx_password)
```
