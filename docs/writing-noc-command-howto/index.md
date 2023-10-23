# Writing NOC Commands

If you need to use a particular piece of code frequently, you can organize it into commands. These commands are executed by calling `./noc <command_name>`.

For instance, to display the version, you can use the command `./noc about`, which is located in the `commands/about.py` file.

```shell
[root@test noc]# ./noc about
22.2+noc-1968.161.9153a970
```

## Command Structure

In general, the structure of a command looks like this:

``` python title="sample.py" linenums="1"
--8<-- "docs/writing-noc-command-howto/sample.py"
```

Let's examine an example in detail.

``` python title="sample.py" linenums="1" hl_lines="1"
--8<-- "docs/writing-noc-command-howto/sample.py"
```

Importing the base class for command.

``` python title="sample.py" linenums="1" hl_lines="2"
--8<-- "docs/writing-noc-command-howto/sample.py"
```

Importing the structure, containing the NOC's version.

``` python title="sample.py" linenums="1" hl_lines="5"
--8<-- "docs/writing-noc-command-howto/sample.py"
```

The implementation of our command should reside within a class derived from the base class `BaseCommand`.

``` python title="sample.py" linenums="1" hl_lines="6"
--8<-- "docs/writing-noc-command-howto/sample.py"
```

The entry point for your command is within the `handle` function. Therefore, we must override this function to define our command's behavior.

``` python title="sample.py" linenums="1" hl_lines="7"
--8<-- "docs/writing-noc-command-howto/sample.py"
```

The `BaseCommand.print()` function is used to print output to stdout when developing custom commands. It is recommended to always use this function instead of the built-in `print()` function within your commands.

In this case, we are using it to print the version information.

``` python title="sample.py" linenums="1" hl_lines="10 11"
--8<-- "docs/writing-noc-command-howto/sample.py"
```

This part of the code is common to all commands and is responsible for launching our command from the command line.

## Example with Argument Parsing

As an example, we will extract the code for checking configured metrics into a command. We will add the ability to pass a list of metrics as parameters. The code will be placed in the `commands/check-metrics.py` file.

``` python title="check-metrics.py" linenums="1"
--8<-- "docs/writing-noc-command-howto/check-metrics.py"
```

Let's run the following:

``` shell
[root@test noc]# ./noc check-metrics 'Interface | Errors | In'
Checking Interface Metric
Not configured metrics on profile Аплинк:  Interface | Errors | In
Not configured metrics on profile Порт РРЛ:  Interface | Errors | In
```

Let's take a closer look at an example:

``` python title="check-metrics.py" linenums="1" hl_lines="1 2 3"
--8<-- "docs/writing-noc-command-howto/check-metrics.py::13"
```

Let's import the standard Python modules we'll need later.

``` python title="check-metrics.py" linenums="1" hl_lines="5 6 7 8 9 10"
--8<-- "docs/writing-noc-command-howto/check-metrics.py::13"
```

We also need to import some NOC definitions.

``` python title="check-metrics.py" linenums="13" hl_lines="1"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:13:17"
```

The implementation of our command should be within a class called `Command`, derived from the `BaseCommand` base class.

``` python title="check-metrics.py" linenums="13" hl_lines="2"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:13:17"
```

The `add_arguments` function allows us to configure the `argsparse`` command parser and set up parsing of additional arguments.

``` python title="check-metrics.py" linenums="13" hl_lines="3"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:13:17"
```

We configure the argument parser to place the entire command line remainder (`REMAINDER`) into the `metrics` option.

``` python title="check-metrics.py" linenums="17" hl_lines="1"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:17:36"
```

The entry point for the command is in the `handle` function, so we must override it.

``` python title="check-metrics.py" linenums="17" hl_lines="2 3"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:17:36"
```
We check if command line parameters are provided ( `option["metrics"]` ), and if not, we call the `BaseCommand.die()` function. The `die()` function prints an error message to stderr and terminates the command with a system error code.

``` python title="check-metrics.py" linenums="17" hl_lines="4"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:17:36"
```
The `connect()` function establishes a connection to the MongoDB database. It should be executed before any database operations.

``` python title="check-metrics.py" linenums="17" hl_lines="5"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:17:36"
```
We create two empty lists:

- Interface Metrics: `interface_metrics`
- Object Metrics: `object_metrics`

``` python title="check-metrics.py" linenums="17" hl_lines="6"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:17:36"
```
We iterate through the command line parameters ( `option["metrics"]` ), as there can be more than one.

``` python title="check-metrics.py" linenums="17" hl_lines="7"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:17:36"
```
We need to retrieve the object (database record) by its name. In NOC, to fetch a record by name, model methods like `.get_by_name()` are used. In addition to simplifying the code, `.get_by_name()` also provides caching, which can significantly enhance performance.

``` python title="check-metrics.py" linenums="17" hl_lines="8 9 10"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:17:36"
```
If the record is not found, `.get_by_name()` returns `None`. We use the check for `None` to ensure that the user has provided the correct metric name. If the user has provided an incorrect name, we print an error message and move on to processing the next metric.

``` python title="check-metrics.py" linenums="17" hl_lines="11 12 13 14"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:17:36"
```
At this point, we check if the metric scope is `Interface`. If it is, we add the metric to the `iface_metrics` list; otherwise, we add it to `object_metrics`.

``` python title="check-metrics.py" linenums="17" hl_lines="15 16 17"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:17:36"
```
If the user has provided at least one object metric, we call the `check_object_metrics` function and pass the `object_metrics` list as a parameter.

``` python title="check-metrics.py" linenums="17" hl_lines="18 19 20"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:17:36"
```
If the user has provided at least one interface metric, we call the `check_interface_metrics` function and pass the `interface_metrics` list as a parameter.

``` python title="check-metrics.py" linenums="38" hl_lines="1"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:38:51"
```
Now, let's define the `check_object_metrics` function, which takes a list of object metrics as input.

``` python title="check-metrics.py" linenums="38" hl_lines="2"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:38:51"
```

We build a dictionary `mt_check`, where the metric ID is used as the key, and the metric object is stored as the value.

``` python title="check-metrics.py" linenums="38" hl_lines="3 4 5"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:38:51"
```
We retrieve all object profiles where periodic discovery is enabled and metrics are defined.

``` python title="check-metrics.py" linenums="38" hl_lines="6"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:38:51"
```
We create a set `check` based on the keys in `mt_check`. In the future, we will remove the discovered metrics from it.

``` python title="check-metrics.py" linenums="38" hl_lines="7 8 9"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:38:51"
```
We iterate through all the metrics defined in the profile and, if they are present in our `check`, we remove them from the `check` set.

``` python title="check-metrics.py" linenums="38" hl_lines="10 11 12 13 14"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:38:51"
```

If there are remaining metrics in our `check` set, we write a message stating that they are not configured for the profile.

``` python title="check-metrics.py" linenums="53" hl_lines="1"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:53:62"
```
Now, let's define the `check_interface_metrics` function, which takes a list of interface metrics as input.

``` python title="check-metrics.py" linenums="54" hl_lines="2"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:53:62"
```
Now, let's define the `check_interface_metrics` function, which takes a list of interface metrics as input.

``` python title="check-metrics.py" linenums="54" hl_lines="3"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:53:62"
```
We create a set `check` from all the input function parameters.

``` python title="check-metrics.py" linenums="54" hl_lines="4 5 6"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:53:62"
```

We iterate through the metrics defined in the profile, and if they are present in our `check`, we remove them from the `check` set.

``` python title="check-metrics.py" linenums="54" hl_lines="7 8 9 10"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:53:62"
```

If there are remaining metrics in our `check` set, we write a message stating that they are not configured for the profile.

``` python title="check-metrics.py" linenums="65" hl_lines="1 2"
--8<-- "docs/writing-noc-command-howto/check-metrics.py:65:66"
```

This part of the code is common to all commands and is responsible for running our command from the command line.