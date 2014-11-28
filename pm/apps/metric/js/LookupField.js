//---------------------------------------------------------------------
// NOC.pm.metric.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.metric.LookupField");

Ext.define("NOC.pm.metric.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.pm.metric.LookupField",
    requires: ["NOC.pm.metric.Lookup"]
});
