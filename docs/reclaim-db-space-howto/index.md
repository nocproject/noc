# How to Reclaim Database Space

Sometimes it's necessary to reduce the number of documents in MongoDB collections to speed up searches, reduce index sizes, and possibly improve the speed of classifying alarms, excluding those that are too old to reopen. It can also be used to free up space occupied by collections.

## Cleaning Archived Alarms

**Mechanism:** Copying all archived alarms that were closed before a specific date into archive collections, followed by removal from the main collection.

### Configuration

To configure this process, you need to specify the settings in `etc/settings.yml` or in KV Consul (`/Root/noc/bi/alarms_archive_policy`) (make sure it is present in [NOC_CONFIG](../config-reference/index.md#noc_config) in the tower). The settings include:

- `4m` – Keep data for 4 months.
- `5y` – Keep data for 5 years.
- `quarterly` – How often to create new collections. You can experiment with this setting.

By setting it to `quarterly`, you ensure that within a year, you will have 4 archive collections for each quarter. When the closure date of an alarm crosses the quarter boundary, it goes into the next collection.

Available options are:

* `weekly`
* `monthly`
* `quarterly`
* `yearly`
  
```
bi:
  alarms_archive_policy: quarterly
  clean_delay_alarms: 4m
  clean_delay_reboots: 5y
  enable_alarms_archive: true
  enable_managedobjects: true
  enable_reboots: true
  enable_alarms: true
```

After configuring the settings, you should verify that the correct values for the variables have been loaded. You can do this as follows:

```shell
./noc config dump bi
```
This command will display the configuration settings. Here's an example:
```
./noc config dump bi
 
bi:
  alarms_archive_batch_limit: 10000
  alarms_archive_policy: quarterly
  chunk_size: 3000
  clean_delay_alarms: 4m
  clean_delay_reboots: 5y
  enable_alarms: true
  enable_alarms_archive: true
  enable_managedobjects: true
  enable_reboots: true
  extract_delay_alarms: 1h
  extract_delay_reboots: 1h
  extract_window: 1d
  language: en
  query_threads: 10
  reboot_interval: 1M
```

```
./noc bi clean
```

test run without real data deletion.
When running without  ```--force``` key:
```
./noc bi clean
 
[reboots] Cleaned before 2013-11-13 11:32:58.424000 ...
[alarms] Cleaned before 2018-07-15 11:51:58.543000 ...
[managedobjects] Cleaned before 2018-09-13 12:00:07.948000 ...
```
**Attention**: The data WILL BE copied to archive collections `alarms.y*` but WILL NOT BE deleted from the main collection `noc.alarms.archived`.

If you have performed a test run, make sure to clean all archive collections `alarms.y20XX*` to avoid any issues when running the operation again.

```
./noc bi clean --force
```
Real Data Transfer
In a real run, after displaying the dates, there will be a countdown before making any changes. You have time to reconsider.

```
./noc bi clean --force
 
[reboots] Cleaned before 2013-11-13 11:32:58.424000 ...
All data before reboots from collection 2013-11-13 11:32:58.424000 will be Remove..
 
9
 
8
```

To Verify that Everything Worked:

1. Run `./noc mongo` to access MongoDB.
2. Use `show collections;` to list collections and make sure there are no collections starting with `alarms.y`. If they exist, you may have used the command before.
3. Run `db.noc.alarms.archived.find().sort({"timestamp": 1}).limit(1)` to retrieve the `"clear_timestamp"` of the first closed alarm. After cleaning, the time should be later than the cleaning time.
4. Execute `db.noc.alarms.archived.count()` to check the number of documents in the archive alarms collection. Remember this count. After cleaning, verify that the count has decreased.
5. Use `db.alarms.y2018_quarter3.count()` to check the number of documents in the archive collection.
6. Finally, run `./noc bi clean --force` and then analyze the collections in MongoDB.

***Note***: If you decide to drop archive collections, you can drop all `alarm.y*` collections EXCEPT the last one, as it may still contain alarms.

## Event Cleanup

**Operation Mechanism**: All events older than 4 weeks will be dropped. This is the default behavior, but you can specify your own parameter using `--before`, as shown in the code.

```
./noc events clean --before 2019-11-27
```
или
```
./noc events clean --before-days 365
```

### Настройка:
```
./noc events clean
```
It will show how many events ***can be (but will not be)*** dropped during the periods:

``` 
Before is not set, use default
 
[events] Cleaned before 2018-10-15 15:12:35.931421 ...
Interval: 2018-04-30 13:10:59, 2018-05-07 13:10:59; Count: 1
Interval: 2018-05-07 13:10:59, 2018-05-14 13:10:59; Count: 4
------------////////////////////////--------------------------
Interval: 2018-10-08 13:10:59, 2018-10-15 13:10:59; Count: 21131
Interval: 2018-10-15 13:10:59, 2018-10-22 13:10:59; Count: 20412

./noc events clean --force
./noc events clean --force --before 2019-11-07
```
For example, Before and After cleaning:
``` 
./noc mongo – идём в монгу
 
db.noc.events.active.count()
562620
 
db.noc.events.active.count()
427573
```
Everything is ready.

## Clearing Datastreams Collections

**Operation Mechanism**: All documents older than the **N**_ttl parameter specified in the datastream settings will be deleted. If 0 is specified, no deletions will occur. To view the current settings: `./noc config dump datastream`

**Usage**:
```bash
./noc datastream clean --datastream alarm
```
where alarm is the datastream name.

Check the operation:
```
./noc mongo
 db.ds_alarm.stats()
Before:
	"ns" : "noc.ds_alarm",
	"size" : 9083632515,
	"count" : 4675331,
	"avgObjSize" : 1942,
	"storageSize" : 1519890432,
	"freeStorageSize" : 9973760,

./noc datastream clean --datastream alarm

After:
	"ns" : "noc.ds_alarm",
	"size" : 766903963,
	"count" : 389807,
	"avgObjSize" : 1967,
	"storageSize" : 1546620928,
	"freeStorageSize" : 1415208960,

```
The collection size has been reduced, but disk space has not been freed due to MongoDB's working peculiarities.

## MongoDB Compact

Starting from version 4.4, it is possible to compact collections and reclaim space marked as free.

**Caution**: Developers recommend creating backups of the database BEFORE performing such an operation.

**Example**:
```
use noc
db.runCommand({ compact: "ds_alarm", force:true })

{
	"bytesFreed" : 1619468288,
	"ok" : 1,
	"$clusterTime" : {
		"clusterTime" : Timestamp(1648810501, 640),
		"signature" : {
			"hash" : BinData(0,"bVXq9xHXqN3VNYj/qnh/z1ZBzkQ="),
			"keyId" : NumberLong("7029149395098533889")
		}
	},
	"operationTime" : Timestamp(1648810501, 639)
}
```
1.5 GB was freed in this example. This operation can be helpful in critical situations. The most effective compaction can be performed on the following collections:

* `noc.alarms.archived`
* `noc.events.active`
* `ds_*` - if data is updated frequently.

## PostgreSQL

There is no need to delete archived items externally. It may be advisable to monitor the database logs.

## ClickHouse

The mechanism for cleaning archived data is implemented based on the TTL (Time To Live) configuration in the 'Main/Setup/CH Policies' interface.

**Configuration**
Example tables for configuration:

* `raw_cpu`
* `raw_interface`
* `raw_mac`
* `raw_ping`
* `raw_alarms`
* `raw_memory`
* `raw_reboots`
* `raw_environment`

Set TTL as desired, for example, use `30` for `raw_mac`.

**Usage Example**

To view the amount of data that will be removed, use the following command:

```
./noc ch-policy apply --host 0.0.0.0
```


To delete the data, use the `--approve` flag:

```
noc ch-policy apply --host 0.0.0.0 --approve
```
