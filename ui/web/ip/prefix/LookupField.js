//---------------------------------------------------------------------
// NOC.ip.prefix.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.prefix.LookupField");

Ext.define("NOC.ip.prefix.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.ip.prefix.LookupField",
    requires: ["NOC.ip.prefix.Lookup"]
});
