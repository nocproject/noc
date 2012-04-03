//---------------------------------------------------------------------
// NOC.main.user.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.user.LookupField");

Ext.define("NOC.main.user.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.main.user.LookupField",
    requires: ["NOC.main.user.Lookup"]
});
