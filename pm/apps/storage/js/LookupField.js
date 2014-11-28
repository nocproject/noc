//---------------------------------------------------------------------
// NOC.pm.storage.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.storage.LookupField");

Ext.define("NOC.pm.storage.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.pm.storage.LookupField",
    requires: ["NOC.pm.storage.Lookup"]
});
