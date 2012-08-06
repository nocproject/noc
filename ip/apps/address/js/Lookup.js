//---------------------------------------------------------------------
// NOC.ip.address.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.address.Lookup");

Ext.define("NOC.ip.address.Lookup", {
    extend: "NOC.core.Lookup",
    url: "/ip/address/lookup/"
});
