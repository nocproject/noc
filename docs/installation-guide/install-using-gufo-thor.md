# Installing NOC using Gufo Thor

[Gufo Thor](https://docs.gufolabs.com/gufo_thor/) is a simple tool designed 
for quickly setting up and evaluating NOC. It's tailored for new NOC users who want to assess NOC's
capabilities and NOC developers who need a fast development environment. 
Thor takes care of the complexity of NOC management, making the process straightforward.

## Prerequisites

To use Thor, make sure you have the following software packages installed:

- Docker
- docker-compose or the compose plugin
- Python 3.8+

## Installation Methods
### System-Level Installation

For dedicated NOC hosts, use this installation method. 
It installs Thor and all required libraries into the system default location.

``` shell
curl https://sh.gufolabs.com/thor | sh
```

After installation, NOC will be launched,
and your browser will open at [https://go.getnoc.com:32777/](https://go.getnoc.com:32777/)

Log in using the following credentials:

- **Username:** admin
- **Password:** admin

### Python VENV Installation

For evaluation, testing, and development purposes, use this installation method. 
It creates a dedicated Python virtual environment (venv) and isolates Thor along 
with all dependent libraries from other systems.

``` shell
python -m venv .
. ./bin/activate
curl https://sh.gufolabs.com/thor | sh
```

After installation, NOC will be launched,
and your browser will open at [https://go.getnoc.com:32777/](https://go.getnoc.com:32777/)

Log in using the following credentials:

- **Username:** admin
- **Password:** admin

Later, when using Thor, make sure to activate the virtual environment (venv):

``` shell
. ./bin/activate
```

## Using NOC

### Startig NOC

``` shell
gufo-thor up
```

### Stopping NOC

``` shell
gufo-thor stop
```

## Further Reading

Refer to the [Gufo Thor Documentation](https://docs.gufolabs.com/gufo_thor/)
for more in-depth details.