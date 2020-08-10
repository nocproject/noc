//---------------------------------------------------------------------
// NOC.main.soposition.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.soposition.LookupField");

Ext.define("NOC.main.ref.soposition.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.main.ref.soposition.LookupField",
    restUrl: "/main/ref/soposition/lookup/"
});
