//---------------------------------------------------------------------
// NOC.crm.subscriber.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.crm.subscriber.LookupField");

Ext.define("NOC.crm.subscriber.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.crm.subscriber.LookupField",
    requires: ["NOC.crm.subscriber.Lookup"]
});
