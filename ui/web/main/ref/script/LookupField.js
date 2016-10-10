//---------------------------------------------------------------------
// NOC.main.pyrule.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.ref.script.LookupField");

Ext.define("NOC.main.ref.script.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.main.ref.script.LookupField",
    restUrl: "/main/ref/script/lookup/",
    uiStyle: "medium"
});
