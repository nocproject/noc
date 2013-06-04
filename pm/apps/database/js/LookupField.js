//---------------------------------------------------------------------
// NOC.pm.database.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.database.LookupField");

Ext.define("NOC.pm.database.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.pm.database.LookupField",
    requires: ["NOC.pm.database.Lookup"]
});
