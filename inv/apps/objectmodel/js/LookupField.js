//---------------------------------------------------------------------
// NOC.inv.objectmodel.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.objectmodel.LookupField");

Ext.define("NOC.inv.objectmodel.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.inv.objectmodel.LookupField",
    requires: ["NOC.inv.objectmodel.Lookup"]
});
