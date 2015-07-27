//---------------------------------------------------------------------
// NOC.main.pool.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.pool.LookupField");

Ext.define("NOC.main.pool.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.main.pool.LookupField",
    requires: ["NOC.main.pool.Lookup"]
});
