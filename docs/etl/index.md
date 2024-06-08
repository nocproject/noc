# ETL (Extract-Transfer-Load)

Extracting inventory information from an external system enables the automation of adding equipment and configuring NOC. The system includes support for the ETL (Extract-Transform-Load) mechanism to facilitate this process. Key terminology includes:

* **Remote System:** The data source for ETL operations.
* **Extractor:** A Python module responsible for extracting information from the Remote System and transforming it into a format suitable for further processing.
* **Loader:** The loading adapter that creates entities in NOC and generates a mapping file.
* **Mappings:** Establishes a connection between IDs in different systems (NOC IDs <> External System IDs).
* **Data Model:** Describes the composition and structure of data for loader operations.
* **Model:** The NOC data model that the loader interacts with.

To interact with ETL, the `./noc etl` command is available. When executed at the base path (`/var/lib/noc/import/`), it creates the following folder structure:

* `import.jsonl.gz`: The file containing the latest extraction.
* `archive`: A folder containing files from previous extractions.
* `mappings.csv`: A file that maps External System IDs to NOC IDs.
* `import.csv.rej.gz`: A file with rejected extraction records (discarded entries).

```
/var/lib/noc/import/<RemoteSystemName>/
├── administrativedomain
│   ├── archive
│   ├── import.jsonl.gz
│   └── mappings.csv
├── container
│   ├── archive
│   ├── import.jsonl.gz
│   └── mappings.csv
├── link
│   └── archive
├── managedobject
│   ├── archive
|   │   ├── import-2021-04-13-23-17-08.jsonl.gz
|   │   ├── import-2021-09-05-16-26-45.jsonl.gz
|   │   └── import-2021-09-05-18-08-45.jsonl.gz
│   ├── import.csv.gz
│   ├── import.csv.rej.gz
│   ├── import.jsonl.gz
│   └── mappings.csv
├── managedobjectprofile
│   ├── archive
│   ├── import.jsonl.gz
│   └── mappings.csv
├── networksegment
│   ├── archive
│   ├── import.jsonl.gz
│   └── mappings.csv
├── networksegmentprofile
│   ├── archive
│   └── import.jsonl.gz
├── resourcegroup
│   ├── archive
│   └── mappings.csv
└── ttsystem
    ├── archive
    ├── import.jsonl.gz
    └── mappings.csv
```

!!! info

    The path `/var/lib/noc/import` is configured using the [path.etl_import](../config-reference/path.md#etl_import) setting.

In summary, the ETL mechanism works as follows:

1. Implement an **extraction adapter** (`extractor`). Its role is to retrieve data from an **external system** and provide it in the format defined by the `loader`. For more details, see the [Loader](#loader) section.
2. Configure the [Remote System](../concepts/remote-system/index.md) in the interface and select the implemented `loaders`.
3. After configuration, execute the command `./noc etl extract <remote_system_name>`. This extracts information from the external system using the adapter created in step 1. All data is stored in files named `import.csv.gz` within the directory `/var/lib/noc/import/<remote_system_name>/<loader_name>/import.csv.gz`.
4. Use the `./noc etl check <remote_system_name>` command to verify the integrity of the extraction.
5. Employ the `./noc etl diff <remote_system_name>` command to review changes compared to the previous extraction file. In the first run, all objects will appear as new.
6. Finally, execute the `./noc etl load <remote_system_name>` command to load the data into NOC. This process creates objects according to the selected loader.

Upon completion, the `import.csv.gz` file is moved to the `/var/lib/noc/import/<remote_system_name>/<loader_name>/archive/import_date.csv.gz` folder, and the `mappings.csv` file is updated to establish a connection between the External System IDs and NOC IDs. Additionally, the `Remote System` and `Remote ID` fields in objects are populated based on the extraction.

## Supported Models

For each of the available system entities, a data model is described. It specifies the fields and data types 
that can be extracted. The [PyDantic](https://pydantic-docs.helpmanual.io) library is used for this purpose. 
The models are located in the `<noc_base>/core/etl/models` directory. They inherit from the base class `BaseModel`, 
and the `Reference` type is used for fields that have a relationship with other entities. Optional fields are 
indicated as `Optional`:

``` python
class AdministrativeDomain(BaseModel):
    id: str
    name: str
    parent: Optional[Reference["AdministrativeDomain"]]
    default_pool: Optional[str]

    _csv_fields = ["id", "name", "parent", "default_pool"]
```

## Extraction Adapter

The procedure of extracting data from an external system and mapping it to a data model is called extraction (`extract`). 
To perform this operation, an adapter is required, where the requested information is translated into the format of the data model. 
The adapter specifies the external system class and data retrieval classes (which implement the work with individual data models). 
For example:

```python

class ZBRemoteSystem(BaseRemoteSystem):
    """
    Base Extraction Class

    The base class for extraction. To maintain order, let's describe the variables available for use in the RemoteSystem Environment:

    Configuration variables (Main -> Setup -> Remote System -> Environments)
    API_URL - URL zabbix web interface
    API_USER - username for ro access to device
    API_PASSWORD - password for user access
    GROUPS_FILTER - list groups for extract
    """

@ZBRemoteSystem.extractor
class ZBAdministrativeDomainExtractor(BaseExtractor):
    """
    Extracting Administrative Domains

    To extract Administrative Domains, we support a hierarchy 
    by specifying the parent Administrative Domain (Parent). 
    It's essential to ensure that parent Administrative Domains 
    come before their child domains in the extraction process. 
    This can be achieved by using numerical IDs.
    """

    name = "administrativedomain"
    model = AdministrativeDomain
    data = [["zb.root", u"Zabbix", None]]
```

## External System Adapter

The description begins with the external system class, `ZBRemoteSystem`, which will be referenced in the settings under the `Handler` field.

::: noc.core.etl.remotesystem.base:BaseRemoteSystem

Following that, there's a description of the classes for data processing. It's essential to specify both the *system model* and the *data model* implemented by the class.

::: noc.core.etl.extractor.base:BaseExtractor

In the example of `ZBAdministrativeDomainExtractor`, data is specified directly within the adapter, and the interaction with the external system occurs in the `extract` method. Out of the box, there are several basic adapter implementations available:
  * `Oracle SQL` - for interacting with Oracle databases
  * `MySQL` - for establishing connections with MySQL databases using an SQL query specified in the `SQL` attribute. Requires the `pymsql` library.
  * `FIAS`

The extraction process is initiated with the command `./noc etl extract REMOTE_SYSTEM_NAME <EXTRACTOR_NAME>`, where:

* `REMOTE_SYSTEM_NAME` - the name of the external system, as specified in the previous step
* `<EXTRACTOR_NAME>` - an optional model name for loading

The extracted data is saved in the `import.csv` file in the directory corresponding to the system model's name. When running this command, it connects to the external system, retrieves information, and generates the `import.csv` files in the following path: `<etl_path>/<remote_system_name>/<loader_name>/`

### Calculating Changes and Data Integrity Verification

Following the extraction, the next step is to perform data integrity checks. Links to data obtained for other models with fields of type `Reference` are verified. You can initiate the verification process using the command `./noc etl check <REMOTE_SYSTEM_NAME>`. In case of any issues, an error message is displayed:

```
[noc.core.etl.loader.base] [RS|managedobject] ERROR: Field #4(administrative_domain) == 'administrativedomain' refers to non-existent record: 10106,mos-pma-pta-pta1-sw01#10106,True,,administrativedomain,default,!new,Generic.Host,zb.std.sw,,,2,192.168.3.2,,,,,,,ZB.AUTO,,
[noc.core.etl.loader.base] [RS|managedobject] ERROR: Field #4(administrative_domain) == 'administrativedomain' refers to non-existent record: 10107,mos-pma-lta-lta1-sw01#10107,True,,administrativedomain,default,!new,Generic.Host,zb.std.sw,,,2,192.168.3.4,,,,,,,ZB.AUTO,,
```

The message provides details about the field (`administrative_domain`), the model it references, and the record with an error.

You can check for changes using the command `./noc etl diff <REMOTE_SYSTEM_NAME> <ExtractorNAME>`. 
The output displays the difference between the new and the last successful extractions. 

The records are marked:

* `/` - modified
* `+` - new
* `-` - removed

```
--- RS.admdiv
--- RS.networksegmentprofile
+ zb.default,zb.default
--- RS.networksegment
+ !new,,Новые,,zb.default
+ !rej,,Отсев,,zb.default
+ !tgfake,,tgfake,,zb.default
--- RS.container
+ 10107,ZabbixHost,PoP | Access,,0,60.646729,56.852081,Екатеринбург, ул. Мира 4
--- RS.resourcegroup
--- RS.managedobjectprofile
+ zb.core.sw,zb.core.sw,35
+ zb.std.sw,zb.std.sw,25
--- RS.administrativedomain
+ zb.root,Заббикс,
--- RS.authprofile
+ ZB.AUTO,ZB.AUTO,,S,,,,,
+ snmp.default,snmp.default,,G,,,,public,
--- RS.ttsystem
--- RS.managedobject
+ 10106,mos-pma-pta-pta1-sw01#10106,True,,zb.root,default,!new,Generic.Host,zb.std.sw,,,2,192.168.3.2,,,,,,,ZB.AUTO,
+ 10107,mos-pma-lta-lta1-sw01#10107,True,10107,zb.root,default,!new,Generic.Host,zb.std.sw,,,2,192.168.3.4,,,,,,,ZB.AUTO,
--- RS.link
--- RS.subscriber
--- RS.serviceprofile
--- RS.service

```

An additional key, `summary`, allows you to view the total number of changes.

`./noc etl diff --summary REMOTE_SYSTEM_NAME <ExtractorNAME>`
```
              Loader |      New |  Updated |  Deleted
              admdiv |        0 |        0 |        0
networksegmentprofile |        1 |        0 |        0
      networksegment |        3 |        0 |        0
           container |        1 |        0 |        0
       resourcegroup |        0 |        0 |        0
managedobjectprofile |        2 |        0 |        0

```

## Loader

The final step is to load the changes into NOC. Loaders for models are located in the `core/etl/loader` folder, 
where files with loader classes are stored. For example, in the loader for `ManagedObject`, the following attributes are defined:

* `name` - the loader's name
* `model` - a reference to the implemented system model
* `data_model` - a reference to the data model
* `purge` method - allows you to override the system's behavior when deleting. In the example, instead of removing the device from the system, it is transitioned to unmanaged status, and the container reference is cleared.

```python

class ManagedObjectLoader(BaseLoader):
    """
    Managed Object loader
    """

    name = "managedobject"
    model = ManagedObjectModel
    data_model = ManagedObject

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clean_map["pool"] = Pool.get_by_name
        self.clean_map["fm_pool"] = lambda x: Pool.get_by_name(x) if x else None
        self.clean_map["profile"] = Profile.get_by_name
        self.clean_map["static_service_groups"] = lambda x: [
            str(x.id) for x in ResourceGroup.objects.filter(remote_id__in=x)
        ]
        self.clean_map["static_client_groups"] = lambda x: [
            str(x.id) for x in ResourceGroup.objects.filter(remote_id__in=x)
        ]

    def purge(self):
        """
        Perform pending deletes
        """
        for r_id, msg in reversed(self.pending_deletes):
            self.logger.debug("Deactivating: %s", msg)
            self.c_delete += 1
            try:
                obj = self.model.objects.get(pk=self.mappings[r_id])
                obj.is_managed = False
                obj.container = None
                obj.save()
            except self.model.DoesNotExist:
                pass  # Already deleted
        self.pending_deletes = []

```

**Loading** the extracted data into NOC is done using the `./noc etl load <REMOTE_SYSTEM_NAME>` command. The procedure works as follows:

1. Adding and modifying records occurs in the order they appear.
2. Deletion of records occurs at the end (after modifications and additions).
3. The mapping file of external system and local identifiers is updated at the end of the extraction.
4. Deletion is performed according to the `purge` method of the loader.

!!! warning

    It is important to understand that changes are calculated relative to the previous load (previous state) from the external system. For this reason, if changes are made to a field in NOC, the load will not roll back those changes. Also, if you lose archived files from the last extraction, all objects will be recreated.

## Portmapper

The Portmapper is a special adapter where rules for mapping ports in the external system to `ManagedObject` interfaces in NOC are defined. It is used in linking based on data from the external system [portmapper](../discovery-reference/box/nri.md).
