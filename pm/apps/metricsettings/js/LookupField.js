//---------------------------------------------------------------------
// NOC.pm.metricsettings.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.metricsettings.LookupField");

Ext.define("NOC.pm.metricsettings.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.pm.metricsettings.LookupField",
    requires: ["NOC.pm.metricsettings.Lookup"]
});
