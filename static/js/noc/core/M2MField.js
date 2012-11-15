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
    autoScroll: true,
    delimiter: ",",
    typeAhead: true,
    triggerAction: "all",
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
        me.callParent();
    },

    setValue: function(value) {
        var me = this;
        if(value === undefined) {
            return;
        }

        if(me.store.loading) {
            // Value will actually be set
            // by store.load callback.
            // Ignore it now
            return me;
        }

        var fromStore = me.fromField.boundList.getStore();
        var toStore = me.toField.boundList.getStore();
        me.store.load({
            scope: me,
            callback: function(records, operation, success) {
                if(success) {
                    fromStore.removeAll();
                    toStore.removeAll();
                    fromStore.loadRecords(records);
                    me.setRawValue(value);
                }
            }
        });
    }
});
