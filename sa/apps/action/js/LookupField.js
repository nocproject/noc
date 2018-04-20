//---------------------------------------------------------------------
// NOC.sa.action.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.action.LookupField");

Ext.define("NOC.sa.action.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.sa.action.LookupField",
    requires: ["NOC.sa.action.Lookup"]
});
