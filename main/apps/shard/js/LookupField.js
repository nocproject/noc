//---------------------------------------------------------------------
// NOC.main.shard.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.shard.LookupField");

Ext.define("NOC.main.shard.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.main.shard.LookupField",
    requires: ["NOC.main.shard.Lookup"],
    uiStyle: "medium"
});
