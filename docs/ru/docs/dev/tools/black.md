# black

[black](https://github.com/psf/black) is the uncompromising Python code formatter.
NOC DevTeem uses black to ensure consistent code Python code formatting and
[PEP8](https://www.python.org/dev/peps/pep-0008/) compliance.

`black` is mandatory check running on every `git push` to the repo.
Every error found considered fatal and CI pipeline will be stopped
immediately until the code will be reformatted properly.

Please refer [How to Setup black Formatter in PyCharm](howto-setup-black-in-pycharm.md)
to integrate `black` with [PyCharm](pycharm.md).

## Docker Container

NOC DevTeam maintains docker container
[registry.getnoc.com/infrastructure/noc-py-lint:master](https://code.getnoc.com/infrastructure/noc-py-lint/container_registry),
containing actual version of `prettier` tool.
