---
template: index.html
title: NOC
hide:
  - navigation
  - toc
hero:
    title: NOC Project
    subtitle: The NOC is the scalable, high-performance and open-source network management system for ISP, service and content providers
    install_button: Getting Started
    source_button: Source Code
highlights:
  - title: Discovery
    description: >
      Advanced network topology discovery across multiple protocols, 
      including configuration and resource usage. It ensures synchronization between 
      your inventory and the network's real-time state, providing accurate insights and control.    
    link: discovery
  - title: Inventory
    description: >
      Centralized database of physical and logical resources.
      Tracks physical assets like chassis and modules. Tracks
      logical resources (IP, VLAN, Phone Numbers) usage as well.
      IP address planning via IPAM
    link: inventory
  - title: Configuration Management
    description: >
      Streamlines network configuration control. It automates backups, tracks changes, 
      and ensures compliance. With versioning and rollback features, it simplifies updates, 
      enhancing network reliability and security.
    link: configuration-management
  - title: Fault Management
    description: >
      Root Cause Analysis, topology correlation, escalation.
      Active probing and passive alarm condition detection
      in syslog and SNMP traps.
    link: fault-management
  - title: Performance Management
    description: >
      Flexible metrics collection via SNMP and CLI.
      Long-term metrics storage. Automatic configuration of dashboards.
      Complex threshold control with window functions.
    link: performance-management
  - title: Service Activation
    description: >
      Effortless device interaction through telnet, 
      SSH, web, TL1, MML, and SNMP interfaces for seamless service activation.
    link: service-activation
  - title: Network Automation
    description: >
      Unlock the potential of network automation with our comprehensive framework,
      featuring an easy-to-use Python API. Streamline tasks, orchestrate processes, 
      and achieve greater efficiency in managing your network infrastructure."
    link: network-automation
  - title: Integration
    description: >
      Plays nice with others. NOC is a part of your infrastructure.
      ETL interface allows to import data from existing systems.
      DataStream API and NBI interfaces provide services to other system.
    link: integration
  - title: Vendor-agnostic
    description: >
      Break free from vendor limitations. With support for 100+ vendors and ongoing expansion, 
      experience true vendor-agnostic solutions for flexible network management
    link: vendor-agnostic
  - title: Open-source
    description: >
      Embrace the power of open source. NOC is distributed under the BSD License,
      fostering collaboration within a vibrant and extensive community
    link: open-source
  - title: Microservices Architecture
    description: >
      Microservices architecture with flexible processing pipelines 
      offers great amount of flexibility, customization and load balancing.
    link: microservices
  - title: Webscale
    description: >
      Scale as you go. Starting from simple single-node installation
      and up to clusters controlling world’s largest networks with a million of objects.
    link: webscale
  - title: Big Data
    description: >
      Introduces Big Data analysis to the Network Management. 
      Builtin analytics database and provided BI tools allows to
    link: big-data    
---
Welcome to the NOC! 

The NOC is the scalable, high-performance and open-source network management system for ISP,
service and content providers

{{ show_highlights(page.meta.highlights) }}

## Documentation Structure

Documentation is organized into into four major parts:

- [Guides](sections-overview/guides.md): Brief introduction for new users.
- [Reference](sections-overview/references.md): Technical reference.
- [How-to guides](sections-overview/howto.md): Step-by-step guides covering common problems.
- [Background](sections-overview/background.md): Clarification and discussion of key topics.

## Community

Getting involved in the NOC community offers you a direct path to establish connections with other skilled and like-minded engineers. It's an opportunity to raise awareness about the fascinating work you're engaged in and hone your skills. Discover more about how you can participate in our community by referring to our [Community Guide](community-guide/index.md).

## License
NOC is open-source software and licensed under the terms of [permissive open-source license](license.md).