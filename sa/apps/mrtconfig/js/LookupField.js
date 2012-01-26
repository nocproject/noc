//---------------------------------------------------------------------
// NOC.sa.mrtconfig.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.mrtconfig.LookupField");

Ext.define("NOC.sa.mrtconfig.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.sa.mrtconfig.LookupField",
    requires: ["NOC.sa.mrtconfig.Lookup"]
});
