//---------------------------------------------------------------------
// NOC.dns.dnsserver.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.dns.dnsserver.LookupField");

Ext.define("NOC.dns.dnsserver.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.dns.dnsserver.LookupField",
    requires: ["NOC.dns.dnsserver.Lookup"]
});
