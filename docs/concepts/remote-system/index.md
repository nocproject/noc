# Remote System

In NOC, basic ETL functionality is implemented, allowing you to extract data from an external system (Remote System) and create objects in NOC based on this data. Currently, the following entities can be loaded:

* Administrative Domains [Administrative Domain](../administrative-domain/index.md)
* Managed Objects [Managed Object](../managed-object/index.md)
* Managed Object Profiles [Managed Object Profile](../managed-object-profile/index.md)
* Segments [Segments](../network-segment/index.md)
* Points of Presence [PoP](../container/index.md)
* Authentication Profiles (`Auth profile`)
* Services [Services](../service/index.md)
* Subscribers [Subscribers](../subscriber/index.md)
* Links - for establishing connections based on external system data [NRI](../../discovery-reference/box/nri.md)
* Resource Groups [Resource Group](../resource-group/index.md)

Briefly, the mechanism works as follows:

1. The extraction adapter [extractor](../../etl/index.md) is implemented. Its task is to obtain data from the external system and provide it in the form of a list of fields defined in the `loader` [Loader](../../etl/index.md).
2. Configure the 'External System' and select the implemented 'loaders' in the interface.
3. After configuration, execute the command `./noc etl extract <remote_system_name>`. This extracts information from the external system (using the adapter written in step 1). Everything is stored in the 'import.csv.gz' files in the '/var/lib/noc/import/<remote_system_name>/<loader_name>/import.csv.gz' directory.
4. Use the command `./noc etl check <remote_system_name>` to check the integrity of the extraction.
5. Use the command `./noc etl diff <remote_system_name>` to view changes compared to the previous extraction file. The first time, all objects will be shown as new.
6. Use the command `./noc etl load <remote_system_name>` to upload the data to NOC (objects corresponding to the loader are created).

After completion, the 'import.csv.gz' file is moved to the '/var/lib/noc/import/<remote_system_name>/<loader_name>/archive/import_date.csv.gz' folder, and the 'mappings.csv' file is updated with the linkage: 'External System ID' <-> 'NOC ID'. Also, the 'Remote System' and 'Remote ID' fields of the objects are populated by the extraction.

<!-- prettier-ignore -->
!!! info
    The path '/var/lib/noc/import' is set by the 'path' -> 'etl_import' setting.

## Working with External Systems

### Configuration of the External System

Configuration starts in the 'Main' -> 'Setup' -> 'Remote Systems' menu. After clicking the 'Add' button, a form for creating an external system with the following items opens:

* Name - the name of the external system. It will be used when working with the 'ETL' command. It is advisable to choose a short name without spaces.
* Description - description (some text).
* Handler - a reference to the [extraction adapter](../../etl/index.md) as a Python import string.
  > Example: 'noc.custom.etl.extractors.zabbix.ZBRemoteSystem' assumes that the file is located in the [custom](../../custom/index.md) folder at the path '<custom_folder>/etl/extractor/zabbix.py'.
* Extractors/Loaders - a list of available models for loading. *Requires implementation in the adapter.*
* Environment - adapter loading settings (passed to it during operation).

### Integration Settings

In objects that support creation from the 'ETL' mechanism, the following fields are also present:

* External System - indicates from which external system the object came.
* External System ID - a text field for the object's ID in the external system.

<!-- prettier-ignore -->
!!! note
    The 'External System' and 'External ID' fields are populated automatically. Manual changes are not recommended.

After configuring the external system, further work is done with the [./noc etl](../../man/etl.md) command.

## API for Retrieving Bindings with External Systems

[NBI Mapper](../../nbi-api-reference/getmappings.md)
