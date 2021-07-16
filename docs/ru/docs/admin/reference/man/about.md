# ./noc about

`about`: Display current version

## Synopsis
```
noc about
```


## Description

`about` dumps NOC version to stdout.
Version format:
```
<major>.<minor>[.<fix>][+<branch>][.<commit_number>.<changeset>]
```

Where:

* `<major>`: Major version
* `<minor>`: Minor version
* `<fix>`: Fix number
* `<branch>`: Branch name, if not master
* `<commit_number>`: Sequental commit number. May be changed during merge operations
* `<changeset>`: Git changeset number

## Examples
```
/opt/noc$ ./noc about
15.05.1
/opt/noc$ ./noc about
15.05.1+dv-ensure-indexes.8268.b7bbd896
```

## See also
