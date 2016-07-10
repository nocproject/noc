//---------------------------------------------------------------------
// NOC.maintainance.maintainancetype.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.maintainance.maintainancetype.LookupField");

Ext.define("NOC.maintainance.maintainancetype.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.maintainance.maintainancetype.LookupField",
    requires: ["NOC.maintainance.maintainancetype.Lookup"]
});
