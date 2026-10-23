# NOC SA Profiles — Agent Guidelines

## Scope
This zone covers the NOC device profiles system used to manage network equipment via software adapters. The matching key is `<vendor>/<software>`: a single software profile can be shared across multiple hardware models that speak the same protocol/config schema.

### Directory Structure
```bash
sa/profiles/
└── <vendor>/               # Vendor or source (e.g., Cisco, MikroTik, Aruba...)
    └── <software>/         # Software/OS name (e.g., IOS, Junos... reusable across models)
        ├── profile.py      # Device adapter — complete interaction logic for this vendor/software pair
        └── *.py            # Helper scripts called by the adapter or CLI tools
```

Current coverage: 108+ vendors mapped to specific software profiles.

## Architecture

### Lookup — no fallback chains
Profiles are matched strictly via the explicit `<vendor>/<software>` path. If a matching profile exists for a combination, its `profile.py` is loaded; otherwise, NOC fails to communicate with the device. There is no generic vendor-level or system-wide default adapter falling back on unmatched pairs—each device must have an exact match.

### profile.py Convention
The file `sa/profiles/<vendor>/<software>/profile.py` is a full device-specific adapter containing class-level attributes mapped to NOC's internal representation:

| Attribute | Purpose | Example Value |
|-----------|---------|---------------|
| `config_commands` | SNMP GET commands for config extraction | `{"running-config": ".1.3.6.1.4.1..."}` |
| `version_command` | SNMP command for OS version detection | `".1.3.6.1.2.1.1.1.0"` (sysDescr) |
| `metric_oids` | Performance measurement OID mappings | Custom SNMP/OID tuples per counter |
| `snmp_trap_handlers` | SNMP trap processing logic | Callback classes or dicts |

The adapter is comprehensive — it defines everything needed to configure, query, and monitor that specific device type. Helper scripts in the same directory may support the adapter but should not replace the core logic.

### Sharing Profiles Across Models
Multiple hardware models can reference the same `<software>/` profile if they share the same configuration schema (e.g., both Cisco 2900 and Cisco 3800 running IOS use `sa/profiles/cisco/ios/profile.py`). When a new model shares an existing software, only the inventory/model definition needs to point at the pre-existing directory.

## Common Patterns
When writing or modifying profiles:
- **Software-first lookup:** Always check for an existing `<software>/` directory with a matching adapter before creating a new one.
- **Adapters are all-or-nothing:** `profile.py` handles every protocol command, OID mapping, and validation rule for that device class. Do not split logic across multiple modules unless you're just creating helpers invoked from the adapter itself.
- Keep adapters strictly Pythonic — no Django template injection or Jinja2 templating in the profile layer.
