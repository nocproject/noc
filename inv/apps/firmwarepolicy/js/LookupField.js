//---------------------------------------------------------------------
// NOC.inv.firmwarepolicy.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.firmwarepolicy.LookupField");

Ext.define("NOC.inv.firmwarepolicy.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.inv.firmwarepolicy.LookupField",
    requires: ["NOC.inv.firmwarepolicy.Lookup"]
});
