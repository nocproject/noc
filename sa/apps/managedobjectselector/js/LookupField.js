//---------------------------------------------------------------------
// NOC.sa.managedobjectselector.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobjectselector.LookupField");

Ext.define("NOC.sa.managedobjectselector.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.sa.managedobjectselector.LookupField",
    requires: ["NOC.sa.managedobjectselector.Lookup"]
});
