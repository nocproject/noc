# NOC 26-dev [Unreleased]

This changelog covers the upcoming NOC 26 release, which has not yet been released. It will be updated continuously as development progresses.

## Highlights

### NOC Pro Foundation

NOC 26 lays the foundation for NOC Pro, an enhanced edition available to all subscription customers. Compared to the standard NOC edition, NOC Pro is designed to provide stronger security, support for more robust cryptographic protocols, and improved scalability. This establishes the foundation for meeting more demanding security and deployment requirements in enterprise and large-scale environments.

### JavaScript Build Pipeline

NOC 26 introduces a new build pipeline for the JavaScript frontend. Previously, the UI loaded a large number of individual JavaScript files following the traditional Ext JS convention. The new pipeline bundles the code into optimized JavaScript assets, removes unused code, and enables efficient browser caching. As a result, the NOC application loads in under one second, while smaller bundles improve the experience on slow network connections, particularly for field engineers. Build-time JavaScript checks also help catch errors earlier.

### Modern HTTP Serving and Security

NOC 26 replaces Uvicorn with Granian as the ASGI server for Starlette, simplifying the deployment architecture and reducing the number of infrastructure components. Granian's built-in static file serving eliminates the need for a separate static file server, while its HTTP/2 support lays the groundwork for modernizing inter-service communication. This architectural evolution also paves the way for introducing mutual TLS (mTLS) between NOC services, strengthening security through authenticated and encrypted internal connections.

### Python 3.13 and Runtime Modernization

NOC 26 moves to Python 3.13, accompanied by extensive code modernization, updated dependencies, improved typing, and a transition from Motor to the asynchronous PyMongo client. These changes establish a more modern and maintainable foundation for future development.

### ARM64 (AArch64) Support

Starting with NOC 26, the platform supports the ARM64 (AArch64) architecture across physical hosts, virtual machines, and containers. This enables deployment on modern ARM-based servers and cloud instances, offering greater flexibility in infrastructure selection and access to energy-efficient computing platforms. The support extends to the entire NOC stack, including its dependent services and databases, with native ARM64 binaries wherever applicable. NOC can also run natively on Apple Silicon Macs, enabling development and testing without x86 emulation.

### Kafka-Only Messaging

The legacy NATS and Liftbridge stack has been fully retired. NOC 26 uses Kafka as its sole inter-service messaging transport, simplifying the architecture and eliminating the need to deploy and maintain legacy components.

### MongoDB 9 Support

NOC 26 advances the database platform to MongoDB 9, modernizing the data storage layer and aligning the platform with the latest MongoDB generation. The upgrade is accompanied by updated database drivers, compatibility improvements, and migration support to ensure a smooth transition from earlier MongoDB versions.

### Expanded Operating System Support [Draft]

NOC 26 expands operating system support to include Debian 13, Ubuntu 26.04 LTS, and AlmaLinux 9, providing more deployment options across modern Linux environments, from traditional servers to cloud infrastructure.

### Fault Management and Alarm Processing

Alarm handling gains escalation profiles, alarm watching, alarm-action APIs, service diagnostics, and additional ETL mappings. These improvements extend the tools available for managing alarms and analyzing service health.

### Expanded Network Device and Vendor Support

NOC 26 adds and improves support for a broad range of network equipment, including BDCOM, D-Link, Juniper, HP/Aruba, Eltex, QTECH, Maipu, Cisco, and ODU devices. Updates cover interface discovery, device-specific events, configuration processing, and additional hardware capabilities.

### Authentication and Security Enhancements

New capabilities include mutual TLS (mTLS), API-key authorization, protection against repeated failed login attempts, and forced password changes. Authentication and secret management have also been refined.

### Proactive Dependency Security

NOC 26 introduces routine vulnerability scanning of project dependencies. Identified vulnerabilities are reviewed and addressed promptly, helping keep dependencies up to date and reduce exposure to known security issues.

### Deployment and Packaging Modernization

NOC 26 streamlines installation and development workflows, introduces `uv`-based package installation, builds Docker images for individual release tags, and drops support for obsolete operating system versions.

## Breaking Changes

### Device Profile Pager Configuration

Device profiles must define pager handling with `pattern_more` as a list of `(pattern, command)` pairs. Check custom device profiles for `command_more` declarations or string/bytes values assigned directly to `pattern_more` and update them before upgrading; profile loading now raises `RuntimeError` for these legacy forms.

Before:

```python
class Profile(BaseProfile):
    pattern_more = rb"^--More--"
    command_more = b" "
```

After:

```python
class Profile(BaseProfile):
    pattern_more = [(rb"^--More--", b" ")]
```

### Device Profile Binary Attributes

Custom device profiles must define the following attributes with `bytes` values:

- `command_submit`
- `pattern_username`
- `pattern_password`
- `pattern_super_password`
- `pattern_prompt`
- `pattern_unprivileged_prompt`
- `pattern_syntax_error`
- `pattern_operation_error`
- `username_submit`
- `password_submit`
- `command_super`

The optional attributes `pattern_super_password`, `pattern_unprivileged_prompt`, `pattern_syntax_error`, `pattern_operation_error`, `username_submit`, `password_submit`, and `command_super` may remain `None`. Check custom profiles and prefix string values with `b`, as shown here:

```python
command_submit = b"\n"
```

Text values are no longer converted automatically and are incompatible.

### Dynamic Dashboard Templates Movement

Built-in dynamic dashboard templates have moved into the web application. If you have custom dynamic dashboard templates, move them from `<custom root>/templates/ddash` to
`<custom root>/services/web/apps/pm/ddash/templates`.

