# Tools

## PyCharm IDE

NOC DevTeam leverages [PyCharm IDE](https://www.jetbrains.com/pycharm/)
gracefully provided by [JetBrains](https://www.jetbrains.com/)
under the terms of [OpenSource Support Program](https://www.jetbrains.com/community/opensource/).

### flake8

NOC CI uses [flake8](http://flake8.pycqa.org/en/latest/) to enforce code style.

To set up flake8 external tool select
`Preferences` > `Tools` > `External Tools`.
Press `+` button. Fill the form:

- `Name`: `flake8`
- `Program`: `/usr/local/bin/docker`
- `Arguments`: `run --rm -w /src -v $ProjectFileDir$:/src registry.getnoc.com/infrastructure/noc-py-lint:master /usr/local/bin/flake8 $FileDirRelativeToProjectRoot$/$FileName$`
- `Working Directory`: `$ProjectFileDir$`
- `Open console for tool output`: Check

Press `Ok`

To check current file select
`Tools` > `External Tools` > `flake8`

### black

NOC uses [black](https://black.readthedocs.io/en/stable/) for automatic code
formatting and codestyle enforcing.

To set up black external tool select
`Preferences` > `Tools` > `External Tools`.
Press `+` button. Fill the form:

- `Name`: `black format`
- `Program`: `/usr/local/bin/docker`
- `Arguments`: `run --rm -w /src -v $ProjectFileDir$:/src registry.getnoc.com/infrastructure/noc-py-lint:master /usr/local/bin/black $FileDirRelativeToProjectRoot$/$FileName$`
- `Working Directory`: `$ProjectFileDir$`
- `Open console for tool output`: Check

Press `Ok`

To format current file select
`Tools` > `External Tools` > `black format`
