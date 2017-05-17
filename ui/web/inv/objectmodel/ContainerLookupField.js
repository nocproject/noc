//---------------------------------------------------------------------
// NOC.inv.objectmodel.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.objectmodel.ContainerLookupField");

Ext.define("NOC.inv.objectmodel.ContainerLookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.inv.objectmodel.ContainerLookupField",
    query: {
        is_container: 1
    }
});
