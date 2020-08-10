//---------------------------------------------------------------------
// NOC.main.soform.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.soform.LookupField");

Ext.define("NOC.main.ref.soform.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.main.ref.soform.LookupField",
    restUrl: "/main/ref/soform/lookup/"
});
