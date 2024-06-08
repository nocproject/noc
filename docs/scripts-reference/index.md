# Scripts Reference

## Script Implementation

The implementation of interfaces and interaction with equipment is carried out in script files. By inheriting the class `noc.core.script.base.BaseScript`, the logic for working with equipment and normalizing received data for transmission to NOC is implemented in these files.

## List of Scripts

| Script Name                                             | Interface                | Generic   | Purpose                                                               |
| ------------------------------------------------------- | ------------------------ | --------- | --------------------------------------------------------------------- |
| [get_version](get_version.md)                           | `IGetVersion`            | {{ no }}  | Retrieve the device's version and platform information                |
| [get_capabilities](get_capabilities.md)                 | `IGetCapabilities`       | {{ yes }} | Collect information about the device's functional support (protocols) |
| [get_config](get_config.md)                             | `IGetConfig`             | {{ no }}  | Retrieve device configuration                                         |
| [get_interfaces](get_interfaces.md)                     | `IGetInterfaces`         | {{ yes }} | Request a list of interfaces from the device                          |
| [get_inventory](get_inventory.md)                       | `IGetInventory`          | {{ yes }} | Collect information about the device's inventory                      |
| [get_chassis_id](get_chassis_id.md)                     | `IGetChassisid`          | {{ yes }} | Retrieve the device's chassis MAC address                             |
| [get_fqdn](get_fqdn.md)                                 | `IGetFqdn`               | {{ yes }} | Retrieve the device's hostname                                        |
| [get_mac_address_table](get_mac_address_table.md)       | `IGetMACAddressTable`    | {{ yes }} | Retrieve the device's MAC address table                               |
| [get_arp](get_arp.md)                                   | `IGetArp`                | {{ yes }} | Retrieve the device's ARP table                                       |
| [get_cdp_neighbors](get_cdp_neighbors.md)               | `IGetCDPNeighbors`       | {{ yes }} | Retrieve the CDP protocol neighbor table                              |
| [get_fdp_neighbors](get_fdp_neighbors.md)               | `IGetFDPNeighbors`       | {{ yes }} | Retrieve the FDP protocol neighbor table                              |
| [get_huawei_ndp_neighbors](get_huawei_ndp_neighbors.md) | `IGetHuaweiNDPNeighbors` | {{ yes }} | Retrieve the Huawei NDP protocol neighbor table                       |
| [get_lacp_neighbors](get_lacp_neighbors.md)             | `IGetLACPNeighbors`      | {{ yes }} | Retrieve the LACP protocol neighbor table                             |
| [get_lldp_neighbors](get_lldp_neighbors.md)             | `IGetLLDPNeighbors`      | {{ yes }} | Retrieve the LLDP protocol neighbor table                             |
| [get_udld_neighbors](get_udld_neighbors.md)             | `IGetUDLDNeighbors`      | {{ yes }} | Retrieve the UDLD protocol neighbor table                             |

## Script Structure

Example script file:

```python
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re


class Script(BaseScript):
    name = "Huawei.VRP.get_version"
    cache = True
    interface = IGetVersion

    def execute_cli(self, **kwargs):
        v = self.cli("display version")
        ...

    def execute_snmp(self, **kwargs):
        v = self.snmp.get("1.XXXX")
        ...

```

## Script Structure

1. **Import Area**: In this section, we import the script's base class (line 1) and the interface implemented by the script (line 2). This is also where you can import any necessary modules for the script, like the regular expression support module (line 3).
2. After importing the required modules, we declare the `Script` class, inheriting it from the base class (`BaseScript`). We specify the full script name, interface, and whether caching the execution result is needed.
3. **Cache**: Setting it to `True` caches the script's execution result. This can be useful when calling the script from other scripts via `self.scripts.<script_name>()`.
4. Methods for interacting with equipment - `execute_snmp()` and `execute_cli()`. The order of execution is determined by priority. You can set the priority in the [ManagedObject](../concepts/managed-object/index.md) settings.
5. If there's an `execute()` method, execution always starts with it, even if `execute_snmp()` or `execute_cli()` are present. This can be used to intervene in determining the execution priority.

## Interaction with Equipment

The base class `noc.core.script.base.BaseScript` includes methods for working with equipment:

### CLI

A text-based interface for working with equipment, implemented via `Telnet` or `SSH`. The `BaseScript.cli` method allows you to execute commands on the equipment. Commands are passed as text arguments, and the output of the requested command is returned as a text string. Further handling is the responsibility of the developer.

- Method: `noc.core.script.base.BaseScript.cli`

In case of a command execution error, an exception (`Exception`) may be raised:
- `CLISyntaxError`: Command error, determined based on the `pattern_syntax_error` setting.
- `CLIOperationError`: Command error, determined based on the `pattern_operation_error` setting.

You can catch these exceptions and use them to alter the script's behavior.

### SNMP

The methods allow you to perform SNMP requests to the equipment, with the OID (Object Identifier) as an argument. The result is returned as a number or a string.

::: noc.core.script.snmp.base:SNMP.get
    selection:
        docstring_style: restructured-text
    rendering:
        show_root_heading: true
        heading_level: 4
        show_category_heading: true

::: noc.core.script.snmp.base:SNMP.getnext
    selection:
        docstring_style: restructured-text
    rendering:
        show_root_heading: true
        heading_level: 4
        show_category_heading: true

To simplify the SNMP interaction you may use `mib`

::: noc.core.script.snmp.base:SNMP.get_table
    selection:
        docstring_style: restructured-text
    rendering:
        show_root_heading: true
        heading_level: 4
        show_category_heading: true

::: noc.core.script.snmp.base:SNMP.get_tables
    selection:
        docstring_style: restructured-text
    rendering:
        show_root_heading: true
        heading_level: 4
        show_category_heading: true

**To facilitate working with SNMP, there is a built-in "mib" module that allows you to convert textual names into corresponding OIDs. To do this, the name must be present in the "cmibs" database, which is located in `<base_noc>/cmibs`. Here's how to add a MIB to "cmibs":**

1. **Prepare the MIB file**: Make sure you have a text file with a `.mib` extension containing the MIB definitions. This file can be an official MIB provided by the device manufacturer or a custom MIB that you want to use.

2. **Create a directory for the MIB**: Inside the `<base_noc>/cmibs` directory, create a new directory with a name that corresponds to the MIB identifier, such as `1.3.6.1.4.1.9.2`.

3. **Copy the MIB file**: Place the MIB file into the created directory. Ensure that the file has the correct name, matching the MIB identifier. For example, if the MIB identifier is `1.3.6.1.4.1.9.2`, the filename should be `1.3.6.1.4.1.9.2.mib`.

4. **Update the MIB database**: Execute the `./noc mib update` command from the command line in the NOC directory. This command updates the MIB database and makes the new MIBs available for use.

You can now use textual names from this MIB in your SNMP queries using the `mib` module. The `mib` module allows you to perform the conversion from a textual name to the corresponding OID using the `mib.resolve(name)` function.

Here is an example of how to use the `mib` module:

```python
from noc.core.mib import mib

mib["BRIDGE-MIB::dot1dBasePortIfIndex"]
: '1.3.6.1.2.1.17.1.4.1.2'
mib["BRIDGE-MIB::dot1dBasePortIfIndex", 100]
: '1.3.6.1.2.1.17.1.4.1.2.100'

```

To interpret SNMP data stored as OctetString correctly, you may need to define the interpretation function through the display_hints argument. Built-in functions for this purpose are available in the noc.core.snmp.render module. By using these functions, you can convert raw OctetString data into human-readable format, making it easier to work with SNMP data.

```python
from noc.core.script.base import BaseScript
from noc.core.mib import mib
from noc.core.snmp.render import render_bin

class Script(BaseScript):

    ...

    def execute_snmp(self, **kwargs):
        ...
        
        for oid, ports_mask in self.snmp.getnext(
            mib["Q-BRIDGE-MIB::dot1qVlanCurrentEgressPorts"],
            display_hints={mib["Q-BRIDGE-MIB::dot1qVlanCurrentEgressPorts"]: render_bin},
        ):
           ...
```

The HTTP module in NOC allows you to perform GET and POST requests to interact with network devices using HTTP. To make HTTP requests, you provide a URL as an argument, and the module returns the response. If an error occurs during the HTTP request, it raises an HTTPError exception (noc.core.script.http.base.HTTPError).

::: noc.core.script.http.base:HTTP.get
    selection:
        docstring_style: restructured-text
    rendering:
        show_root_heading: true
        heading_level: 4
        show_category_heading: true

::: noc.core.script.http.base:HTTP.post
    selection:
        docstring_style: restructured-text
    rendering:
        show_root_heading: true
        heading_level: 4
        show_category_heading: true

When making an HTTP request, you have the option to use the "Basic" authentication scheme by setting the `use_basic` parameter to `True`. More complex authentication schemes are implemented using the "Middleware" mechanism. Middleware is an intermediate handler that receives the request before it's sent, allowing you to modify the request data or headers. Built-in handlers can be found in the `noc.core.script.http.middleware.*` module, and to apply them, you need to specify their names in the `http_request_middleware` setting in the [SA profile](../concepts/sa-profile/index.md). To enable Middleware, the following settings are available in the profile:

- `enable_http_session`: Authenticates once per session.
- `http_request_middleware`: A list of Middleware handlers to apply.

For example, to use "Digest" authentication, you can add `digestauth` to your `profile.py`:

```python

    enable_http_session = True
    http_request_middleware = [
        "digestauth",
    ]
```

If necessary, you can add custom middleware handlers for your profile. These handlers inherit from the `BaseMiddleware` class and should be placed in the `<profile>/middleware/` folder. To use your custom middleware, add an import statement in the `http_request_middleware` setting in the profile:

For example:

```python

# Python modules
import orjson
import hashlib
import codecs

# NOC modules
from noc.core.script.http.middleware.base import BaseMiddleware
from noc.core.http.client import fetch_sync
from noc.core.comp import smart_bytes


class AuthMiddeware(BaseMiddleware):
    """
    Append HTTP Digest authorisation headers
    """

    name = "customauth"

```


### MML

The Machine Messaging Language (MML) protocol is used for machine-to-machine data exchange and is commonly used in various telephony systems, such as Private Branch Exchanges (PBX).

### RTSP

The Real-Time Streaming Protocol (RTSP) is used for streaming media, particularly in video surveillance systems, including cameras and video recorders, to control the flow of video streams. It also allows for requesting information about available streams. For example, to obtain the status of an RTSP port, you can use the following format:


```python
from noc.core.script.base import BaseScript
from noc.core.script.rtsp.error import RTSPConnectionRefused, RTSPAuthFailed


class Script(BaseScript):

    ...

    def execute(self, **kwargs):
        ...
        
        try:
            check = self.rtsp("DESCRIBE", "/Streaming/Channels/101/")
        except RTSPConnectionRefused:
            check = 0
```


## Generic Scripts
A set of scripts is already implemented in a generic form using SNMP. They are available within the Generic profile located at `<noc_base>/sa/profiles/Generic``. You can use the functionality of these scripts by inheriting them and overriding their behavior through attributes. For example, if your equipment supports SNMP, you can use inheritance to implement the get_interfaces script as follows:

```python
# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "<profile_name>.get_interfaces"
    interface = IGetInterfaces

```

In this case, the functionality of the base script will be sufficient.

## Customization

### Example Scripts

self.profile

* Huawei.VRP.get_version 

.. literalinclude:: ../examples/get_version.py
                            :language: python

* Huawei.VRP.get_capabilities

.. literalinclude:: ../examples/get_capabilities.py
                            :language: python


.. _rst-application-label:


### Script Base Class


::: noc.core.script.base:BaseScript
    selection:
        docstring_style: restructured-text
        members: true
        filters:
          - "!_x_seq"
          - "!__call__"
          - "!__init__"
          - "!apply_matchers"
          - "!clean_input"
          - "!clean_output"
          - "!run"
          - "!compile_match_filter"
          - "!match"
          - "!call_method"
          - "!root"
          - "!get_cache"
          - "!set_cache"
          - "!schedule_to_save"
          - "!push_prompt_pattern"
          - "!pop_prompt_pattern"
          - "!get_timeout"
          - "!get_cli_stream"
          - "!close_cli_stream"
          - "!close_snmp"
          - "!get_mml_stream"
          - "!close_mml_stream"
          - "!get_rtsp_stream"
          - "!close_rtsp_stream"
          - "!close_current_session"
          - "!close_session"
          - "!get_access_preference"
          - "!get_always_preferred"
          - "!to_reuse_cli_session"
          - "!to_keep_cli_session"
          - "!push_cli_tracking"
          - "!push_snmp_tracking"
          - "!iter_cli_fsm_tracking"
          - "!request_beef"
    rendering:
        heading_level: 4
        show_source: false
        show_category_heading: true
        show_root_toc_entry: false
        show_if_no_docstring: true

.. automodule:: noc.core.script.base
    :members:
    :undoc-members:
    :show-inheritance:

.. _rst-interfaces-label:


### NOC Interfaces

The profile sends data to the main system through a data exchange interface. The interface describes the format and set of data that a script implementing it should return. There are several interfaces available for profile implementation:

::: noc.sa.interfaces.igetversion:IGetVersion
    rendering:
      show_source: true

::: noc.sa.interfaces.igetinterfaces:IGetInterfaces
    selection:
      docstring_style: restructured-text
    rendering:
      show_source: true

.. automodule:: noc.sa.interfaces.igetversion
    :members:
    
.. automodule:: noc.sa.interfaces.igetcapabilities
    :members:

.. automodule:: noc.sa.interfaces.igetinterfaces
    :members:
    :show-inheritance:

.. automodule:: noc.sa.interfaces.igetchassisid
    :members:

.. automodule:: noc.sa.interfaces.igetfqdn
    :members:

.. automodule:: noc.sa.interfaces.igetlldpneighbors
    :members:

.. automodule:: noc.sa.interfaces.igetcdpneighbors
    
    .. autoclass:: IGetCDPNeighbors
    
.. automodule:: noc.sa.interfaces.igetarp
    :members:

.. automodule:: noc.sa.interfaces.igetmacaddresstable
    :members:

.. automodule:: noc.sa.interfaces.igetconfig
    :members:

.. automodule:: noc.sa.interfaces.igetinventory
    :members:

.. _rst-interface-data-type-label:

### Interface Data Types

In the interfaces, the following data types are applied:

.. automodule:: noc.sa.interfaces.base
    :members:
