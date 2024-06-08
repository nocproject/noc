# DS Filter

This interface allows the creation of custom datastreams [Datastream](../datastream-api-reference/index.md) based on the built-in ones. It enables the formation of custom streams based on one of the basic ones. When calculating changes, the `DS Filter` is called, and the processed record is passed to it. The returned value is written to a new `datastream`. The settings are located in the menu `Main -> Setup -> DataStream Config`.

DS Filters are applied during the calculation of data from the source (`source`) datastream.

    ds_filter(data_record):
        Implements Datastream Filter
    
        :param data_record: Source datastream data record
        :returns: new data

## Examples

### Return Data

```python
    import datetime
    from noc.sa.models.managedobject import ManagedObject

    def ds_filter(data_record):
        mo = ManagedObject.get_by_id(data_record["id"])
        ts = datetime.datetime.now()
        yield {"managed_object": mo.bi_id, "name": mo.name, "ip": mo.address, "ts": ts.strftime("%Y-%m-%d %H:%M:%S")}

```