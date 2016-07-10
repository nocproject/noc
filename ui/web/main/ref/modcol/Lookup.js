//---------------------------------------------------------------------
// NOC.main.ref.modcol.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.ref.modcol.Lookup");

Ext.define("NOC.main.ref.modcol.Lookup", {
    extend: "NOC.core.Lookup",
    fields: ["id", "label", "table", "collection"],
    url: "/main/ref/modcol/lookup/"
});
