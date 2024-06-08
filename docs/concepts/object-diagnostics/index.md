# Object Diagnostics

When working with systems with a large number of settings, users often have questions about why a particular functionality is not working.
Especially for newcomers when the documentation is incomplete and the settings are not obvious (distributed across multiple locations).
Traditionally, in such cases, users turn to other users or specialists with questions.
Usually, most inquiries end with recommendations to enable a specific setting and check the log for magical strings.
As a result, a simple action takes a significant amount of time.
To simplify the understanding of the system's operation, the **Diagnostics** (`Diagnostic`) functionality is designed for devices.

**Diagnostics** - a sequence of **checks** (`Check`) to determine the current use of functionality.
The result of the checks can be one of 4 states (`State`):

* **Enabled** - the functionality is successfully used
* **Blocked** - the functionality is disabled by system settings
* **Failed** - a failure occurred during the use of the functionality
* **Unknown** - the functionality is not engaged

## User Interface

In the user interface of diagnostics, **indicators** (`indicator`) are presented that display the current state.
The indicator displays the name of the diagnostics, and the color encodes the states:

* *Enabled* - green
* *Failed* - orange
* *Blocked* - gray
* *Unknown* - the indicator is not displayed

![Managed Object Indicators](diagnostics_indicators_form1.png)

## Diagnostics

Diagnostics in the system can be divided into **internal** - occupied by checking the operation of the system's functions
and **user** - added through the user interface.
The difference between them is only in the settings - the first ones are specified in the code,
and the second ones are available for modification and are located in the `Service Activation -> Setup -> (Object Diagnostic Configuration)` menu.

![Diagnostic Config Form](object_diagnostic_config_create_web1.png)

* **Name** - the name of the diagnostics. Displayed on the indicator
* **Description** - description of the diagnostics
* **Display Order** - priority of indicator display
* **Show in form** - display the indicator on the device form
* Check Policy
    * *Any* - for success, it is sufficient to pass any check
    * *All* - to succeed, all checks must pass
* **Checks** - list of checks
    * *Check* - check name
    * *Argument* - parameter for the check. Interpretation depends on the check
* **Depends on Diagnostics** - dependency on diagnostics. The result of the listed diagnostics will be included in the check
* Launch Parameters
    * Run on full discovery
    * Run on periodic
    * **Run Policy**
        * *Always* - every poll
        * *When failed* - first time, then on failure
    * **Run Order**
        * *On start* at the beginning of the poll
        * *On end* at the end of the poll
* **Alarm Class** - raise an alarm on diagnostics failure (transition to the `failed` state)
* **Alarm Labels** - add labels to the alarm
* **Save in History** - save the results of checks in history
* **Device Check Rules** - allow specifying on which devices to run diagnostics

!!! note
    For diagnostics launched at the **end of polling**: if an error occurs at the previous stage, the diagnostics will not be started!


### Built-in Diagnostics

The system already includes several diagnostics that are launched *at the start* of full discovery (`Box Discovery`) and check the operation with equipment.

#### PROFILE

Checks the correctness of the `SA Profile` selection for the device. Settings:

* The `Profile` checkbox in the object profile settings enables/disables diagnostics
* Profile check rules are in (`Profile Check Rules`)

#### SNMP

Checks the access credentials for SNMP. Can use multiple access credentials when access rules are available. Settings:

* Access preference priority. If `Access Preference - CLI Only`, diagnostics are blocked
* Allow access credentials selection. Allows the use of access credential selection rules during access setup

#### CLI

Checks the access credentials for TELNET/SSH. Can use multiple access credentials when access rules are available. Settings:

* Access preference priority. If `Access Preference - SNMP Only`, diagnostics are blocked
* Allow access credentials selection. Allows the use of access credential selection rules during access setup

#### Access

Comprehensive diagnostics include `CLI`, `SNMP`, and `HTTP`. To work correctly, all incoming access protocols are required.


#### SNMPTRAP and SYSLOG

Sets the fact of receiving an `SNMP Trap` or `Syslog` for the device. It triggers when the first SNMP Trap or Syslog is received from the device. Settings:

* Syslog/Trap source in device settings
* `Event Process Policy` in device or object profile settings

Table of built-in diagnostics settings 

| Name     | Run Policy        | Checks          | Alarm Class                                      |
| -------- | ----------------- | --------------- | ------------------------------------------------ |
| PROFILE  | Unknown or Failed | PROFILE         | `Discovery &#124 Guess &#124 Profile`            |
| SNMP     | Unknown or Failed | SNMPv1, SNMPv2c | `NOC &#124 Managed Object &#124 Access Lost`     |
| CLI      | Unknown or Failed | TELNET, SSH     | `NOC &#124 Managed Object &#124 Access Lost`     |
| Access   | `---`             | SNMP, CLI       | `NOC &#124 Managed Object &#124 Access Degraded` |
| SNMPTRAP | `---`             | `---`           | `---`                                            |
| SYSLOG   | `---`             | `---`           | `---`                                            |

## Checks

Diagnostics are implemented through checks. The system includes several checks:

* **REMOTE_PING** - Check the availability of the IP address from the device. Requires the **ping** script to be implemented.
* **SNMPv1, SNMPv2c** - Check the `SNMP` access credentials. Uses credentials from the device settings.
* **TELNET, SSH** - Check the `CLI` access credentials for `TELNET` and `SSH`. Uses credentials from the device settings.
* **PROFILE** - Check the device profile based on the rules from the menu.
* **LOCAL_PING** - Check the availability of the IP address from the NOC (activator).

In addition to the built-in checks, users can add custom ones. To do this, it is necessary to connect the custom one and place the code in `core/checkers`.
After restarting the system, they will become available for selection.
