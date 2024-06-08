# SA Profile

# Interaction with Devices in NOC

Interaction with devices in NOC is built through profiles (`SA Profile`).

You can describe the `SA Profile` (`SA Profile`) as an intermediary (adapter).
It receives raw data streams from the equipment and transforms them into data that is passed to NOC for further processing by the system.
Profiles are tightly bound to the software used on the equipment.
Within the profile, you can check the software version and model, but this complicates the script code.
For this reason, profiles are compatible with each other within the framework of one manufacturer's operating system.
For example, different profiles are used for `Cisco IOS` and `Cisco ASA`.

<!-- prettier-ignore -->
!!! note

    `SA Profile` (`SA Profile`) is a component of NOC that hides the specifics of interacting with the equipment from the rest of the system.

Some features of profiles can be highlighted:

* Written in the [Python](https://en.wikipedia.org/wiki/Python) programming language.
* Automatically loaded at system startup (a system restart is required for updates to take effect).
* No restrictions on using any Python modules.
* The `get_version` script is mandatory, while others are added depending on the equipment's capabilities.
* The collected data remains within a single session.

## Structure and Interaction with the System

### Profile Composition

Profiles are located in the `sa/profiles` directory.
According to the convention, the profile's name is constructed from the manufacturer's name `VendorName` and the OS name `OSName`: `Juniper.JUNOS`, `Cisco.IOS`.

```
<noc_base>/sa/profiles/
├── <VendorName>
│   ├── __init__.py
│   ├── <OSName>
│   │   ├── __init__.py
│   │   ├── profile.py
│   │   ├── confdb
│   │   │   ├── __init__.py
│   │   │   └── normalizer.py
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   └── ...
│   │   ├── get_version.py
│   │   ├── get_vlans.py
│   │   ├── ...
│   │   └── snmp_metrics
│   │       ├── cpu_usage_1min.json
│   │       └── ...

```

<!-- prettier-ignore -->
!!! note
    Names are case-sensitive!

The profile itself consists of:

* `profile.py` - A class that implements equipment operation settings, inherited from `noc.core.profile.base.BaseProfile`.
* A set of [scripts](../../scripts-reference/index.md) that implement one of the available *SA Interfaces* (`SA Interface`).
* `snmp_metrics/` - A folder with a list of `SNMP OID`s for scripts.
* `confdb/` - A folder with configuration parsers for [ConfDB](../../confdb-reference/index.md).
* `middleware/` - A folder for handling `HTTP` requests to the equipment.

<!-- prettier-ignore -->
!!! note
    `SA Interface` (`SA Interface`) describes the format and composition of the data that needs to be sent to NOC.

### Interaction with NOC

Interaction with NOC is based on calling profile scripts from other system components: [discovery](../../discovery-reference/box/index.md). The information obtained is used to gather details about the equipment. The information returned by the script must match the specified interface (`SA Interface`). In the system itself, profiles are assigned to a device ([ManagedObject](../../concepts/managed-object/index.md)), so there is no need to explicitly specify the invoked profile; it is taken from the settings. The calling sequence looks like this:

![Profile Calling Diagram](sa-script.png)

1. Calling a script for the `ManagedObject` device. An example of calling the `get_version` script:

    ```python
    
        from noc.core.mongo.connection import connect
        connect()
        from noc.sa.models.managedobject import ManagedObject
    
        mo = ManagedObject.objects.get(name="<MONAME>")
        r = mo.scripts.get_version()
        r
        {'vendor': 'Huawei',
         'platform': 'S2326TP-EI',
         'version': '5.70 (V100R006C05)',
         'image': 'V100R006C05',
         'attributes': {'Serial Number': '21',
          'Patch Version': 'V100R006SPH031'}}
    
    ```
2. After the call, the system makes an `RPC` request to the [SAE](../../services-reference/sae.md) service to obtain the script invocation parameters:
    * Equipment credentials (username, password, Community)
    * Capabilities
    * Profile operation settings ([Access Policy](../../concepts/managed-object-profile/index.md#Access(Доступ)))

3. SAE responds with a redirection code to the appropriate activator [Activator](../../services-reference/activator.md).

4. The activator creates a session and executes the invoked script with the provided parameters.

5. If the script includes `execute_cli` or `execute_snmp` methods, they are called according to their priorities. In the presence of an `execute` method, it is always executed.

6. The results of the script's execution are checked against the interface, and the results are returned to the caller.

7. If an error occurs during execution, the error code is returned.

### SA Interfaces

To transmit results, SA interfaces are used.

A `SA Interface` is a special entity in NOC designed to facilitate interaction between components.

SA interfaces are located in the `sa/interfaces` directory. They are available for specifying in profile scripts. There is also the possibility to define custom interfaces through [Custom](../../custom/index.md).

In a *SA Interface*, the structure of data transmitted and returned by a script is described. The transmitted data includes script parameters, and the returned data includes the results of the script's execution. It specifies:

* Field names
* Data types
* Default values
* Field mandatory status

If the data does not pass validation, an exception is raised. As an example, let's consider the `noc.sa.interfaces.igetversion.IGetVersion` interface.

::: noc.sa.interfaces.igetversion:IGetVersion
    selection:
        docstring_style: restructured-text
        members: true
    rendering:
        heading_level: 4
        show_source: true
        show_root_heading: true
        show_if_no_docstring: true
        show_signature_annotations: true

The description clearly shows what result to expect from the script. In this case, for successful transmission, we need to generate a dictionary (`dict`) with keys:

* `vendor` - a text field `StringParameter()`
* `version` - a text field `StringParameter()`
* `platform` - a text field `StringParameter()`
* `attributes` (optional parameter) - a dictionary, and the list of keys is not limited. This means that the developer can choose what to include in it.

The result looks something like this:
```json
    {
    "vendor": "Cisco",
    "version": "12.4(5)",
    "platform": "IOS",
    "attributes":
                {
                "image": "image.bin",
                "type": "type1",
                "count": 2
                }
    }
```

You can verify the data through the developer console.

```python
r = {
    "vendor": "Cisco",
    "version": "12.4(5)",
    "platform": "IOS",
    "attributes":
                {
                "image": "image.bin",
                "type": "type1",
                "count": 2
                }
    }

from noc.sa.interfaces.igetversion import IGetVersion
IGetVersion().clean_result(r)
{'vendor': 'Cisco',
 'version': '12.4(5)',
 'platform': 'IOS',
 'attributes': {'image': 'image.bin', 'type': 'type1', 'count': 2}}


```

### Equipment Interaction Settings

<!-- prettier-ignore -->
!!! note

    Prior to version 19.1, settings were located in the `__init__.py` file.

The equipment interaction settings are concentrated in the `profile.py` file of the profile. Most settings are described in the base class - `noc.core.profile.base` and are available for override in the profile class. They include the following groups:

* Profile name: It should match the structure - `cisco/ios` - `Cisco.IOS`.
* CLI operation settings: Methods and attributes describing CLI operation.
  * `pattern_prompt` - Prompt string on the equipment.
  * `pattern_syntax_error` - List of error command lines (raises a `CLISyntaxError` exception upon a match).
  * `command_more` - Command (or key) to send to the equipment for page-by-page output (deprecated, use `pattern_more` instead).
  * `command_disable_pager` - Command to disable paging of information.
  * `command_enter_config` - Command to enter configuration mode.
  * `command_leave_config` - Command to exit configuration mode.
  * `command_save_config` - Command to save configuration.
  * `command_exit` - Command to exit the CLI session.
  * `rogue_chars` - List of characters to filter from the command output.
* SNMP operation settings:
  * `snmp_metrics_get_chunk` - Size of SNMP metric request.
  * `snmp_metrics_get_timeout` - Timeout for SNMP request.
* Methods for normalizing output data:
  * `convert_interface_name` - Normalizes the interface name; input is the interface name as it may appear on the equipment, and output is the interface name in the system.
  * `get_interface_type` - Allows getting the type of an interface by its name.
  * `config_volatile` - List of lines in the configuration that need to be filtered out during collection. Usually used to exclude lines that can change in the configuration (e.g., time changes).
* Matchers: Set script attributes when conditions match (software version, platform). Used for executing different commands depending on the software version/model.
* `ConfDB` parser settings:
  * `config_tokenizer` - The applied [Tokenizer](../../confdb-reference/tokenizer.md).
  * `config_normalizer` - The applied [Normalizer](../../confdb-reference/normalizer.md).
  * `config_applicators` - List of [Applicators](../../confdb-reference/index.md).

Example `profile.py` file:

```python
from noc.core.profile.base import BaseProfile
import re


class Profile(BaseProfile):
    name = "Huawei.VRP"
    pattern_more = [
        (r"^  ---- More ----", " "),
        (r"[Cc]ontinue?\S+", "y\n\r"),
        (r"[Cc]onfirm?\S+", "y\n\r"),
        (r" [Aa]re you sure?\S+", "y\n\r"),
        (r"^Delete flash:", "y\n\r"),
        (r"^Squeeze flash:", "y\n\r")
    ]
    pattern_prompt = r"^[<#\[](?P<hostname>[a-zA-Z0-9-_\.\[/`\s]+)(?:-[a-zA-Z0-9/]+)*[>#\]]"
    pattern_syntax_error = r"(Error: |% Wrong parameter found at|% Unrecognized command found at|Error:Too many parameters found|% Too many parameters found at|% Ambiguous command found at)"

    command_more = " "
    config_volatile = ["^%.*?$"]
    command_disable_pager = "screen-length 0 temporary"
    command_enter_config = "system-view"
    command_leave_config = "return"
    command_save_config = "save"
    command_exit = "quit"
    rogue_chars = [
        re.compile(rb"\x1b\[42D\s+\x1b\[42D")
    ]

    matchers = {
        "is_kernel_3": {"version": {"$gte": "3.0", "$lt": "5.0"}},
        "is_kernelgte_5": {"version": {"$gte": "5.0"}},
        "is_bad_platform": {
            "version": {"$regex": r"5.20.+"},
            "platform": {"$in": ["S5628F", "S5628F-HI"]},
        }}
    config_tokenizer = "indent"
    config_normalizer = "VRPNormalizer"
    confdb_defaults = [
        ("hints", "interfaces", "defaults", "admin-status", True),
        ("hints", "protocols", "lldp", "status", True),
    ]
    config_applicators = ["noc.core.confdb.applicator.collapsetagged.CollapseTaggedApplicator"]

    def generate_prefix_list(self, name, pl, strict=True):
        ...

    def convert_interface_name(self, s):
        ...

```

The full list of available methods is accessible in the base profile class - `noc.core.profile.base.BaseProfile`.

### Scripts

A complete description of script functionality is available in the [Scripts Reference](../../scripts-reference/index.md). In this section, we will look at how scripts work within a profile.

The most useful component of a profile is the script. Scripts perform all the meaningful work related to equipment interaction. A script is a Python module file that implements one interface (SA Interface). It inherits from the class `noc.core.script.base.BaseScript` and implements the `execute()` method, which is called when the script is executed. The main components of a script include:

* `name` - the script's name. It follows the template: `<profile_name>.<script_name>`.
* `interface` - a reference to the implemented interface class.
* `execute_snmp()` - called if the execution priority (`access_preference`) is set to `SNMP`.
* `execute_cli()` - called if the execution priority (`access_preference`) is set to `CLI`.
* `execute()` - called at the beginning of execution.

<!-- prettier-ignore -->
!!! note
    Like profiles, scripts are read and cached upon NOC startup. Therefore, to apply changes, a restart is required. This rule does not apply to debugging using `./noc script`.

The `get_version` script is mandatory and is used to obtain basic information about the equipment: manufacturer, software version, and model. The second most important script is `get_capabilities`, which determines the device's support for various protocols (SNMP) and technologies.

<!-- prettier-ignore -->
!!! note
    It is prohibited to use the call to other scripts in the `get_version` and `get_capabilities` scripts; otherwise, a cyclic dependency may occur.

To call a profile method from a script, use the `self.profile.<method_name()>` construction.

### Debugging

For debugging a profile, the `./noc script` tool is used. It allows running scripts from the profile in debug mode. This is done as follows:

``./noc script --debug <script_name> <object_name> <parameters>``, where

* ``<script_name>`` - the full script name (in the format <folder1>.<folder2>.<script_name>)
* ``<object_name>`` - the Object's name (from the Objects -> Object List menu)
* ``<parameters>`` - parameters (optional, only if used)

For convenience, parameters can be passed in a JSON file format, which does not require adding the object to the system.

`./noc script --debug <script_name> <path_to_json_file>`

## BaseProfile class

::: noc.core.profile.base:BaseProfile
    selection:
        docstring_style: restructured-text
        filters:
          - "!add_script_method"
          - "!initialize"
          - "!get_telnet_naws"
          - "!allow_cli_session"
          - "!send_backspaces"
          - "!get_config_tokenizer"
          - "!get_config_normalizer"
          - "!get_confdb_defaults"
          - "!iter_config_applicators"
          - "!iter_collators"
          - "!get_http_request_middleware"
          - "!get_snmp_display_hints"
          - "!get_snmp_response_parser"
          - "!has_confdb_support"
          - "!_get_patterns"
          - "!_get_rogue_chars_cleaners"
          - "!get_snmp_rate_limit"
          - "!cleaned_input"
    rendering:
        heading_level: 3
        show_source: false
        show_category_heading: true
        show_root_toc_entry: false
        members_order: "source"
