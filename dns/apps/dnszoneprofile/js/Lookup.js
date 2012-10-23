//---------------------------------------------------------------------
// NOC.dns.dnszone.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.dns.dnszoneprofile.Lookup");

Ext.define("NOC.dns.dnszoneprofile.Lookup", {
    extend: "NOC.core.Lookup",
    url: "/dns/dnszoneprofile/lookup/"
});
