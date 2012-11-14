//---------------------------------------------------------------------
// NOC.core.M2MField -
// Lookup Many-To-Many form field
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.M2MField");

Ext.define("NOC.core.M2MField", {
    extend: "Ext.ux.form.ItemSelector",
    displayField: "label",
    valueField: "id",
    queryMode: "remote",
    queryParam: "__query",
    queryCaching: false,
    queryDelay: 200,
    forceSelection: true,
    delimiter: ",",
    typeAhead: true,
    triggerAction: "all",
    query: {},
    stateful: false,
    autoSelect: false,
    pageSize: 0,

    initComponent: function() {
        var me = this,
            sclass = me.__proto__.$className.replace("M2MField",
                                                     "Lookup");
        Ext.applyIf(me, {
            store: Ext.create(sclass)
        });
        if(me.query) {
            Ext.apply(me.store.proxy.extraParams, me.query);
        }
        me.addEvents("clear");
        me.callParent();
        me.on("specialkey", me.onSpecialKey, me, {delay: 100});
    },

    setValue: function(value) {
        var me = this;

        if(me.store.loading) {
            // Value will actually be set
            // by store.load callback.
            // Ignore it now
            return me;
        }
        console.log(value);
            // number or string
            // Start store lookup
            // @todo: do not refresh current value
            var v = me.getValue();

            if(!v || v != value) {
                me.store.load({
                    scope: me,
                    callback: function(records, operation, success) {
                        if(success && records.length > 0) {
                            console.log("!!!", records);
                        }
                    }
                });
            }
       
    }
});
