---
tags:
  - how-to
---
# How to Setup black Formatter in PyCharm

NOC uses [black](https://black.readthedocs.io/en/stable/) for automatic code
formatting and code style enforcing.

## Setup External Tool
To set up black external tool select
`Preferences` > `Tools` > `External Tools`.
Press `+` button. Fill the form:

- `Name`: `black format`
- `Program`: `/usr/local/bin/docker`
- `Arguments`: `run --rm -w /src -v $ProjectFileDir$:/src registry.getnoc.com/infrastructure/noc-py-lint:master /usr/local/bin/black $FileDirRelativeToProjectRoot$/$FileName$`
- `Working Directory`: `$ProjectFileDir$`
- `Open console for tool output`: Check

Press `Ok`

## Check Current File
To format current file select
`Tools` > `External Tools` > `black format`

## Setup Automatic File Formatting
To set up automatic file formatting on save select
`Preference` > `Tools` > `File Watchers`.

Press `+` button. Fill the form:

- `File Type`: `Python Files`
- `Scope`: Press `...` then fill the form:
    - `Name`: `NOC Python Files`
    - `Pattern`: `file:*.py&&file[noc]:*/`
    - Press `Ok`
- `Program`: `/usr/local/bin/docker`
- `Arguments`: `run --rm -w /src -v $ProjectFileDir$:/src registry.getnoc.com/infrastructure/noc-py-lint:master /usr/local/bin/black $FileDirRelativeToProjectRoot$/$FileName$`
- `Working Directory`: `$ProjectFileDir$`

Press `Ok`. Black container will run automatically on every python file save.
