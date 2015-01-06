//---------------------------------------------------------------------
// NOC.support.crashinfo.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.support.crashinfo.LookupField");

Ext.define("NOC.support.crashinfo.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.support.crashinfo.LookupField",
    requires: ["NOC.support.crashinfo.Lookup"]
});
