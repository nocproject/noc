# DS Filter

Интерфейс формирует собственные датастримы [Datastream](../datastream-api-reference/index.md) на основании встроенных.
Позволяет формировать пользовательские потоки на основе одного из базовых. 
При расчёте изменения вызывается `DS Filter` в который передаётся обработанная запись. Вовзращаемое значение записывается в новый `datastream`. 
Настройки находятся в меню `Основные (Main) -> Настройки (Setup) -> DataStream Config`

DS Filter применяются во время расчёта данных исходного (`source`) датастрима (`Datastream`).

    ds_filter(data_record):
        Implements Datastream Filter
    
        :param data_record: Source datastream data record
        :returns: new data

## Примеры

### Вернуть данные 

```python
    import datetime
    from noc.sa.models.managedobject import ManagedObject

    def ds_filter(data_record):
        mo = ManagedObject.get_by_id(data_record["id"])
        ts = datetime.datetime.now()
        yield {"managed_object": mo.bi_id, "name": mo.name, "ip": mo.address, "ts": ts.strftime("%Y-%m-%d %H:%M:%S")}

```