//---------------------------------------------------------------------
// NOC.main.pyrule.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.ref.probehandler.Lookup");

Ext.define("NOC.main.ref.probehandler.Lookup", {
    extend: "NOC.core.Lookup",
    fields: ["id", "label", "description", "form", "solution", "tags"],
    url: "/main/ref/probehandler/lookup/"
});
