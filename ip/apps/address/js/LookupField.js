//---------------------------------------------------------------------
// NOC.ip.address.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.address.LookupField");

Ext.define("NOC.ip.address.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.ip.address.LookupField",
    requires: ["NOC.ip.address.Lookup"]
});
