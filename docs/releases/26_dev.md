# NOC 26-dev [Unreleased]

This changelog covers the upcoming NOC 26 release, which has not yet been released. It will be updated continuously as development progresses.

## Highlights

### JavaScript Build Pipeline

NOC 26 introduces a new build pipeline for the JavaScript frontend. Previously, the UI loaded a large number of individual JavaScript files following the traditional Ext JS convention. The new pipeline bundles the code into optimized JavaScript assets, removes unused code, and enables efficient browser caching. As a result, the NOC application loads in under one second, while smaller bundles improve the experience on slow network connections, particularly for field engineers. Build-time JavaScript checks also help catch errors earlier.

### Kafka-Only Messaging

The legacy NATS and Liftbridge stack has been fully retired. NOC 26 uses Kafka as its sole inter-service messaging transport, simplifying the architecture and eliminating the need to deploy and maintain legacy components.

### Python 3.13 and Runtime Modernization

NOC 26 moves to Python 3.13, accompanied by extensive code modernization, updated dependencies, improved typing, and a transition from Motor to the asynchronous PyMongo client. These changes establish a more modern and maintainable foundation for future development.

### Fault Management and Alarm Processing

Alarm handling gains escalation profiles, alarm watching, alarm-action APIs, service diagnostics, and additional ETL mappings. These improvements extend the tools available for managing alarms and analyzing service health.

### Expanded Network Device and Vendor Support

NOC 26 adds and improves support for a broad range of network equipment, including BDCOM, D-Link, Juniper, HP/Aruba, Eltex, QTECH, Maipu, Cisco, and ODU devices. Updates cover interface discovery, device-specific events, configuration processing, and additional hardware capabilities.

### Authentication and Security Enhancements

New capabilities include mutual TLS (mTLS), API-key authorization, protection against repeated failed login attempts, and forced password changes. Authentication and secret management have also been refined.

### Deployment and Packaging Modernization

NOC 26 streamlines installation and development workflows, introduces `uv`-based package installation, builds Docker images for individual release tags, and drops support for obsolete operating system versions.