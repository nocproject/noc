//---------------------------------------------------------------------
// NOC.sa.managedobject.TreeField
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.TreeField");

Ext.define("NOC.sa.administrativedomain.TreeField", {
    extend: "NOC.core.TreeField",
    alias: "widget.sa.administrativedomain.TreeField",
    restUrl: '/sa/administrativedomain'
});
