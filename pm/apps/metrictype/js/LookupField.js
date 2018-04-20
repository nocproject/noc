//---------------------------------------------------------------------
// NOC.pm.metrictype.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.metrictype.LookupField");

Ext.define("NOC.pm.metrictype.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.pm.metrictype.LookupField",
    requires: ["NOC.pm.metrictype.Lookup"]
});
