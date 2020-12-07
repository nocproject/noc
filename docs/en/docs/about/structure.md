# NOC Manual Organization

This document provides an overview of the global organization of the
documentation resource. Refer to the notes below if you are having
trouble understanding the reasoning behind a file's current location,
or if you want to add a new documentation but aren't sure how to
integrate it into the existing resource.

If you have any questions or suggestions regarding the documentation,
join the
[NOC Docs](https://t.me/nocdocs) telegram channel.

## Global Organization

### Index
`mkdocs.yml` file holds all documentation project configuration, including
the topics structure. Every markdown file should be enumerated in the `nav`
section.

### Documentation section
Documentation split in following sections:

* `Reference` - technical description of machinery and how to operate it.
* `Admin's Guide` - technical references for a system administrators.
* `Developer's Guide` - technical references for system developers.
* `Tutorials` - Step-by-step lessons for beginners.
* `HOWTO` - Step-by-step answers to the practical questions.
* `Release Notes` - NOC Release notes.
* `About` - Common information about the project.
