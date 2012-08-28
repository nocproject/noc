//---------------------------------------------------------------------
// NOC.peer.as.Lookup 
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.as.Lookup");

Ext.define("NOC.peer.as.Lookup", {
    extend: "NOC.core.Lookup",
    model: "NOC.peer.as.Model",
    url: "/peer/as/lookup/"
});
