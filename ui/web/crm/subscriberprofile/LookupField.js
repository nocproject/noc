//---------------------------------------------------------------------
// NOC.crm.subscriberprofile.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.crm.subscriberprofile.LookupField");

Ext.define("NOC.crm.subscriberprofile.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.crm.subscriberprofile.LookupField",
    requires: ["NOC.crm.subscriberprofile.Lookup"]
});
