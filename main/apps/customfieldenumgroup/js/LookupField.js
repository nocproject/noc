//---------------------------------------------------------------------
// NOC.main.customfieldenumgroup.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.customfieldenumgroup.LookupField");

Ext.define("NOC.main.customfieldenumgroup.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.main.customfieldenumgroup.LookupField",
    requires: ["NOC.main.customfieldenumgroup.Lookup"]
});
