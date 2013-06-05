//---------------------------------------------------------------------
// NOC.pm.probe.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.probe.LookupField");

Ext.define("NOC.pm.probe.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.pm.probe.LookupField",
    requires: ["NOC.pm.probe.Lookup"]
});
