# Custom

NOC provides extensive capabilities for extending the system's functionality by adding custom code. This allows you to modify the system's behavior within broad limits and compensate for any missing features.

## List of Supported Extensions

The following extensions are supported for the system:

* `bi` - Models for `BI` (Business Intelligence).
* `cmibs` - `CMIBs` (Custom MIBs) files.
* `commands` - Command tools.
* `collections` - Collections.
* `geocoder` - GIS geocoders for external systems.
* `etl` - Data synchronization adapters with external systems [ETL](../etl/index.md).
    * `extractors` - ETL adapters for external systems.
    * `loader` - Custom loaders.
    * `portmappers` - Adapters for mapping interfaces with external systems.
* `handlers` - Directory with handlers [Handlers](../handlers-reference/index.md).
* `sa` - Interaction with devices.
    * `profiles` - SA (Service Activation) profiles [SA Profile](../profiles-reference/index.md).
    * `interfaces` - SA interfaces [SA Interface](../concepts/sa-profile/index.md#SA-Interfaces).
* `services` - System service extensions.
    * `card` - Custom cards [Card](../card/index.md).
    * `web` - Custom web applications [Web](../web/index.md).
    * `nbi` - NBI (Northbound Interface) API endpoint [NBI](../nbi-api-reference/index.md).
* `templates` - `Jinja` templates for various parts of the system.
    * `ddash` - Templates for `PM` (Performance Monitoring) metric graphs.
* `tt` - Adapters for trouble ticket escalation systems (`TroubleTicket`).

## Custom Structure

Extensions are stored separately from the main code and are dynamically loaded by the system at startup. The main requirement is that an extension should occupy a specific place in the file system structure. The root directory for the extension is set through the `custom_path` setting in the `path` section of the global configuration [Custom Path](../config-reference/path.md#custom_path). This setting is made during system installation in the `Tower`. By default, it is located at `/opt/noc_custom`, and the structure looks as follows:

```
.
├── bi
│   └── models
├── cmibs
├── collections
│   ├── fm.alarmclasses
│   └── sa.profiles
├── commands
├── core
│   └── geocoder
├── etl
│   ├── bi
│   ├── extractors
│   ├── loader
│   └── portmappers
├── handlers
│   ├── alarms
├── lib
│   └── app
├── sa
│   ├── interfaces
│   └── profiles
├── services
│   ├── card
│   ├── nbi
│   └── web
├── templates
│   └── ddash
└── tt

```

<!-- prettier-ignore -->
!!! note

    To apply changes in the custom code, it is essential to restart the process (or the entire NOC).
