//---------------------------------------------------------------------
// NOC.main.report.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.pyrule.LookupField");

Ext.define("NOC.main.ref.report.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.main.ref.report.LookupField",
    restUrl: "/main/ref/report/lookup/",
    uiStyle: "medium"
});
