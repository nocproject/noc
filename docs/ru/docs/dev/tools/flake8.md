# flake8

[flake8](https://flake8.pycqa.org/en/latest/) is a statical Python code
checker, combining [PEP8](https://www.python.org/dev/peps/pep-0008/)
code validation and various linters.

`flake8` is mandatory check running on every `git push` to the repo.
Every error found considered fatal and CI pipeline will be stopped
immediately until the bug is fixed.

Please refer [How to Setup flake8 Check in PyCharm](howto-setup-flake8-in-pycharm.md)
to integrate `flake8` with [PyCharm](pycharm.md).

## Docker Container

NOC DevTeam maintains docker container
[registry.getnoc.com/infrastructure/noc-py-lint:master](https://code.getnoc.com/infrastructure/noc-py-lint/container_registry),
containing actual version of `flake8` tool.
