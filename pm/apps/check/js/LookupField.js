//---------------------------------------------------------------------
// NOC.pm.check.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.check.LookupField");

Ext.define("NOC.pm.check.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.pm.check.LookupField",
    requires: ["NOC.pm.check.Lookup"]
});
