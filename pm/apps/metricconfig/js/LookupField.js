//---------------------------------------------------------------------
// NOC.pm.metricconfig.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.metricconfig.LookupField");

Ext.define("NOC.pm.metricconfig.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.pm.metricconfig.LookupField",
    requires: ["NOC.pm.metricconfig.Lookup"]
});
