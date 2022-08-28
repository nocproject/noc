---
tags:
  - how-to
---
# How to Setup flake8 Check in PyCharm
NOC CI uses [flake8](http://flake8.pycqa.org/en/latest/) to enforce code style.

## Setup External Tool
To set up flake8 external tool select
`Preferences` > `Tools` > `External Tools`.
Press `+` button. Fill the form:

- `Name`: `flake8`
- `Program`: `/usr/local/bin/docker`
- `Arguments`: `run --rm -w /src -v $ProjectFileDir$:/src registry.getnoc.com/infrastructure/noc-py-lint:master /usr/local/bin/flake8 $FileDirRelativeToProjectRoot$/$FileName$`
- `Working Directory`: `$ProjectFileDir$`
- `Open console for tool output`: Check

Press `Ok`

## Check Current File
To check current file select
`Tools` > `External Tools` > `flake8`