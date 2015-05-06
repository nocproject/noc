//---------------------------------------------------------------------
// NOC.inv.modelinterface.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.modelinterface.LookupField");

Ext.define("NOC.inv.modelinterface.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.inv.modelinterface.LookupField",
    requires: ["NOC.inv.modelinterface.Lookup"]
});
