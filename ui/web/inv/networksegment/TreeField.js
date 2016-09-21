//---------------------------------------------------------------------
// NOC.sa.managedobject.TreeField
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.networksegment.TreeField");

Ext.define("NOC.inv.networksegment.TreeField", {
    extend: "NOC.core.TreeField",
    alias: "widget.inv.networksegment.TreeField",
    restUrl: '/inv/networksegment'
});
