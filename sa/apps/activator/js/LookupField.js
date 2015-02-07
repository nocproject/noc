//---------------------------------------------------------------------
// NOC.sa.activator.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.activator.LookupField");

Ext.define("NOC.sa.activator.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.sa.activator.LookupField",
    requires: ["NOC.sa.activator.Lookup"],
    uiStyle: "medium"
});
