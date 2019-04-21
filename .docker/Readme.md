Containers
==========

* `registry.getnoc.com/noc/noc/code:$version` -- contains NOC. Ready to be launched as standalone image.

* `registry.getnoc.com/noc/noc/static:$version` -- only contains static files and nginx. Intended to be used as container for frontend static for nomad or k8s

* `registry.getnoc.com/noc/noc/build` -- contains current branch source and dependencies, used as container for tests. Should not be uploaded to registry. 

* `registry.getnoc.com/noc/noc/dev:$version` -- based on code container but contains some additional debug tools.

