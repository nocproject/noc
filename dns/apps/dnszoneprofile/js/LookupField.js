//---------------------------------------------------------------------
// NOC.dns.dnszoneprofile.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.dns.dnszoneprofile.LookupField");

Ext.define("NOC.dns.dnszoneprofile.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.dns.dnszoneprofile.LookupField",
    requires: ["NOC.dns.dnszoneprofile.Lookup"]
});
