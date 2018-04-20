//---------------------------------------------------------------------
// NOC.ip.ippool.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.ippool.LookupField");

Ext.define("NOC.ip.ippool.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.ip.ippool.LookupField",
    requires: ["NOC.ip.ippool.Lookup"]
});
