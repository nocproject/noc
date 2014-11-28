//---------------------------------------------------------------------
// NOC.main.sync.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.sync.LookupField");

Ext.define("NOC.main.sync.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.main.sync.LookupField",
    requires: ["NOC.main.sync.Lookup"]
});
