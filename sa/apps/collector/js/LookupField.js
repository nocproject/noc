//---------------------------------------------------------------------
// NOC.sa.collector.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.collector.LookupField");

Ext.define("NOC.sa.collector.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.sa.collector.LookupField",
    requires: ["NOC.sa.collector.Lookup"]
});
