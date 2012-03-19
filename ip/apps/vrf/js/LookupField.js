//---------------------------------------------------------------------
// NOC.ip.vrf.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.vrf.LookupField");

Ext.define("NOC.ip.vrf.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.ip.vrf.LookupField",
    requires: ["NOC.ip.vrf.Lookup"]
});
