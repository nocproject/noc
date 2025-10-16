//---------------------------------------------------------------------
// NOC.dns.dnszone.RRTypeField
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.dns.dnszone.RRTypeField");

Ext.define("NOC.dns.dnszone.RRTypeField", {
  extend: "Ext.form.ComboBox",
  alias: "widget.dns.dnszone.RRTypeField",
  queryMode: "local",
  store: [
    "A",
    "AAAA",
    "AFSDB",
    "AXFR",
    "CAA",
    "CERT",
    "CNAME",
    "DHCID",
    "DLV",
    "DNAME",
    "DNSKEY",
    "DS",
    "HIP",
    "IPSECKEY",
    "IXFR",
    "KEY",
    "LOC",
    "MX",
    "NAPTR",
    "NS",
    "NSEC",
    "NSEC3",
    "NSEC3PARAM",
    "OPT",
    "PTR",
    "RRSIG",
    "SIG",
    "SPF",
    "SRV",
    "SSHFP",
    "TA",
    "TKEY",
    "TSIG",
    "TXT",
  ],
});
