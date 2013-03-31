//---------------------------------------------------------------------
// NOC.main.stompaccess.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.stompaccess.LookupField");

Ext.define("NOC.main.stompaccess.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.main.stompaccess.LookupField",
    requires: ["NOC.main.stompaccess.Lookup"]
});
