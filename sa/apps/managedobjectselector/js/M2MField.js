//---------------------------------------------------------------------
// NOC.sa.managedobjectselector.M2MField
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobjectselector.M2MField");

Ext.define("NOC.sa.managedobjectselector.M2MField", {
    extend: "NOC.core.M2MField",
    alias: "widget.sa.managedobjectselector.M2MField",
    requires: ["NOC.sa.managedobjectselector.Lookup"]
});
