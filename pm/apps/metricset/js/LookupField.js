//---------------------------------------------------------------------
// NOC.pm.metricset.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.metricset.LookupField");

Ext.define("NOC.pm.metricset.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.pm.metricset.LookupField",
    requires: ["NOC.pm.metricset.Lookup"]
});
