//---------------------------------------------------------------------
// NOC.core.modelfilter.Base
// Boolean model filter
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.modelfilter.Base");

Ext.define("NOC.core.modelfilter.Base", {
    extend: "Ext.container.Container",
    ftype: "base",
    name: null,
    handler: undefined,

    onChange: function() {
        var me = this;
        if(Ext.isDefined(me.handler))
            me.handler();
    },

    getFilter: function() {
        return {};
    }
});
