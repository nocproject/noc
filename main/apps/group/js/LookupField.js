//---------------------------------------------------------------------
// NOC.main.group.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.group.LookupField");

Ext.define("NOC.main.group.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.main.group.LookupField",
    requires: ["NOC.main.group.Lookup"]
});
