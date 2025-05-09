# NOC Shell HOWTO

The system offers extensive customization capabilities tailored to specific user needs—from developing your own hardware adapters and APIs to modifying system behavior by integrating your own code [Handlers] [Link to Custom documentation].

Development is done in the *Python programming language*.

## Developer Console

Python includes a developer console (accessed via `python`), and in NOC, this console is enhanced with internal system modules, providing a convenient tool for developing and testing system extensions.

To launch the developer console, run `./noc shell` from the NOC root directory.

!!! note
    For added convenience, you can install the `ipython` package to extend console capabilities. Install it using `./bin pip install ipython`

After executing `./noc shell`, you'll enter the developer console:

```shell
[root@test noc]# ./noc shell
Python 3.8.3 (default, Jun 18 2020, 20:51:40) 
Type 'copyright', 'credits' or 'license' for more information
IPython 8.5.0 -- An enhanced Interactive Python. Type '?' for help.

In [1]: 
```

You will see the Python version and the `ipython` version, if installed. All system modules are available, and import paths begin with the prefix `noc.`, while modules from [custom] start with `noc.custom.`.  
For example, to check the system version, use the `noc.core.version` module:

```python
In [1]: from noc.core.version import version

In [2]: version.version
Out[2]: '22.2+noc-1968.169.c4875fdb'
```

When starting the console, the system database is **not connected** by default.  
This is convenient for local development of profiles, but data access requires a connection, which can be established using the `noc.core.mongo.connection` module:

```python
In [4]: from noc.core.mongo.connection import connect

In [5]: connect()
[noc.core.mongo.connection] Connecting to MongoDB {'db': 'test', 'username': 'test', 'password': '********', 'authentication_source': 'test', 'replicaSet': 'test', 'readPreference': 'secondaryPreferred', 'maxIdleTimeMS': 60000, 'host': 'mongodb://sova:********@192.168.1.100:27017/test'}

In [6]: 
```

If connecting to the database frequently, typing it each time can become tedious.  
For such cases, `ipython` allows setting startup scripts. These are `.py` files in the `~/.ipython/profile_default/startup/` folder, executed on launch.  
Example file `~/.ipython/profile_default/startup/00-mongo.py`:

```python
from noc.core.mongo.connection import connect
connect()
```

Note: The developer console **does not enforce access permissions**, so care must be taken during bulk updates.

## Accessing System Data

The main unit describing data in the system is the *Model*, which includes:

* Storage location and framework used
* Description of data fields
* Methods for data manipulation

Models are located in `models` subfolders of the system components.  
To *import a model*, specify its path and name:

```python
In [2]: from noc.sa.models.managedobject import ManagedObject
```

!!! note
    Models require a connection to the system `Database` to function.

Models use one of two frameworks:
* `Django` – data stored in `PostgreSQL`
* `MongoEngine` – data stored in `MongoDB`

A list of all system models can be found in `models.py` at the root of the system.  
To determine which framework a model uses, you can use the `is_document` function:

```python
In [2]: from noc.sa.models.managedobject import ManagedObject
In [3]: from noc.models import is_document

In [4]: is_document(ManagedObject)
Out[4]: False
```

The *API* for record manipulation is similar for both frameworks, except for `EmbeddedDocument` in `MongoEngine` models.  
Basic record operations include:

* Record selection and filtering. For filtering by related fields, reference the related instance.  
  More filter expressions are documented in the relevant `Framework` documentation:

```python
In [2]: from noc.sa.models.managedobject import ManagedObject
In [8]: from noc.main.models.pool import Pool

In [11]: ManagedObject.objects.filter(name="21-166506")
Out[11]: <QuerySet [<ManagedObject: 21-166506>]>

In [12]: ManagedObject.objects.filter(name__contains="21-166506")
Out[12]: <QuerySet [<ManagedObject: 21-166506>, <ManagedObject: 21-166506#PE>]>

In [13]: Pool.objects.get(name="default")
Out[13]: <Pool: default>

In [14]: p = Pool.objects.get(name="default")
In [15]: ManagedObject.objects.filter(pool=p)
Out[15]: <QuerySet [<ManagedObject: 20-049475>, <ManagedObject: 21-043981>, <ManagedObject: 21-166201#PE>, <ManagedObject: 21-070948#PE>, <ManagedObject: 21-166506>,<ManagedObject: 20-458751#PE>, '...(remaining elements truncated)...']>
```

* Record deletion. Use the `delete()` method.  
  If the record is referenced elsewhere, a `Referred from model` error will occur:

```python
In [8]: from noc.main.models.pool import Pool

In [10]: p = Pool.objects.get(name="default")
In [14]: p.delete()

ValueError: Referred from model sa.ManagedObject: 20-049475 (id=24484)
```

* Record creation.  
  Create an instance of the appropriate model, populate required fields (`is_required=True`), and call `save()`:

```python
In [16]: p = Pool(name="default2")

In [17]: p.save()
Out[17]: <Pool: default2>
```

## Examples

Let’s look at a few examples of how to perform routine operations using the developer console.

### Create, Modify, and Assign Settings

#### Display configured metrics for Managed Object and Interface profiles

Since metrics are stored as embedded documents, working with *ManagedObject Profile* (uses `Django`) and *Interface Profile* (uses `MongoEngine`) differs.  
Let's start with *ManagedObject Profile*:

```python
# For each profile with metrics enabled, list configured metric names by resolving metric_type IDs
In [30]: from noc.core.mongo.connection import connect
In [31]: from noc.sa.models.managedobjectprofile import ManagedObjectProfile
In [12]: from noc.pm.models.metrictype import MetricType
In [32]: connect()

In [29]: for mop in ManagedObjectProfile.objects.filter(enable_periodic_discovery_metrics=True, enable_periodic_discovery=True):
    ...:     print(f"Configured metrics for {mop.name}: ", ", ".join(MetricType.get_by_id(mc["metric_type"]).name for mc in mop.metrics))
```

Check for missing metrics:

```python
In [30]: from noc.core.mongo.connection import connect
In [31]: from noc.sa.models.managedobjectprofile import ManagedObjectProfile
In [32]: from noc.pm.models.metrictype import MetricType
In [33]: connect()

In [34]: metrics_check = ["CPU | Usage", "Memory | Usage"]
In [35]: mt_check = {str(mt.id) for mt in MetricType.objects.filter(name__in=metrics_check)}

In [36]: for mop in ManagedObjectProfile.objects.filter(enable_periodic_discovery_metrics=True, enable_periodic_discovery=True):
    ...:     checks = set(mt_check)
    ...:     for mc in mop.metrics:
    ...:         if mc["metric_type"] in checks:
    ...:             checks.remove(mc["metric_type"])
    ...:     if not checks:
    ...:         continue
    ...:     print(f"Not configured metrics on profile {mop.name}: ", ",".join(MetricType.get_by_id(c).name for c in checks))
```

Now for *Interface Profile*, it’s simpler due to `EmbeddedDocument`:

```python
In [30]: from noc.core.mongo.connection import connect
In [33]: from noc.inv.models.interfaceprofile import InterfaceProfile
In [34]: connect()

In [36]: for ip in InterfaceProfile.objects.filter(metrics__exists=True):
    ...:     print(ip.name, ", ".join(f"'{mc.metric_type.name}'" for mc in ip.metrics))
```

Check for missing metrics:

```python
In [30]: from noc.core.mongo.connection import connect
In [33]: from noc.inv.models.interfaceprofile import InterfaceProfile
In [34]: connect()

In [35]: metrics_check = ["CPU | Usage", "Memory | Usage"]
In [36]: for ip in InterfaceProfile.objects.filter(metrics__exists=True):
    ...:     checks= set(metrics_check)
    ...:     for mc in ip.metrics:
    ...:         if mc.metric_type.name in checks:
    ...:             checks.remove(mc.metric_type.name)
    ...:     if not checks:
    ...:         continue
    ...:     print(f"Not configured metrics on profile {ip.name}: ", ",".join(MetricType.get_by_name(c).name for c in checks))
```

#### Add metric to profile configuration from a list

From the above validation, you can proceed to modify profile configurations:

Add a metric to *ManagedObject Profile*:

```python
In [30]: from noc.core.mongo.connection import connect
In [31]: from noc.sa.models.managedobjectprofile import ManagedObjectProfile, ModelMetricConfigItem
In [32]: from noc.pm.models.metrictype import MetricType
In [33]: connect()

In [36]: mop = ManagedObjectProfile.objects.get(name="default")
In [37]: mop.metrics += [ModelMetricConfigItem(metric_type=str(MetricType.get_by_name('CPU | Usage').id), enable_periodic=True).dict()]

In [38]: mop.save()
```

Add a metric to *Interface Profile*:

```python
In [30]: from noc.core.mongo.connection import connect
In [31]: from noc.inv.models.interfaceprofile import InterfaceProfile, InterfaceProfileMetrics
In [32]: from noc.pm.models.metrictype import MetricType
In [33]: connect()

In [36]: ip = InterfaceProfile.objects.get(name="default")
In [37]: ip.metrics += [InterfaceProfileMetrics(metric_type=MetricType.get_by_name('Interface | Errors | In'), enable_periodic=True)]

In [38]: ip.save()
Out[60]: <InterfaceProfile: default>
```