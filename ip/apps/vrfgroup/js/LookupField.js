//---------------------------------------------------------------------
// NOC.ip.vrfgroup.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.vrfgroup.LookupField");

Ext.define("NOC.ip.vrfgroup.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.ip.vrfgroup.LookupField",
    requires: ["NOC.ip.vrfgroup.Lookup"]
});
