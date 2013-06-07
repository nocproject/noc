//---------------------------------------------------------------------
// NOC.pm.ts.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.ts.LookupField");

Ext.define("NOC.pm.ts.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.pm.ts.LookupField",
    requires: ["NOC.pm.ts.Lookup"]
});
