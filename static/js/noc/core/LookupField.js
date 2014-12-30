//---------------------------------------------------------------------
// NOC.core.LookupField -
// Lookup form field
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.LookupField");

Ext.define("NOC.core.LookupField", {
    extend: "Ext.form.ComboBox",
    displayField: "label",
    valueField: "id",
    queryMode: "remote",
    queryParam: "__query",
    queryCaching: false,
    queryDelay: 200,
    forceSelection: true,
    minChars: 2,
    typeAhead: true,
    triggerAction: "all",
    query: {},
    stateful: false,
    autoSelect: false,
    pageSize: 25,
    listConfig: {
        minWidth: 240
    },
    isLookupField: true,

    initComponent: function() {
        var me = this,
            // Get store class name
            sclass = me.$className.replace(".LookupField", ".Lookup");
        Ext.apply(me, {
            store: Ext.create(sclass)
        });
        if(me.query) {
            Ext.apply(me.store.proxy.extraParams, me.query);
        }
        me.callParent();
        me.on("specialkey", me.onSpecialKey, me, {delay: 100});
    },

    getLookupData: function() {
        return this.getDisplayValue();
    },

    onSpecialKey: function(field, e) {
        var me = this;
        if(e.keyCode == e.ESC) {
            me.clearValue();
            me.fireEvent("clear");
        }
    }
});
