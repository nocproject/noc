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
        me.restUrl = me.store.url;
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
        switch(e.keyCode) {
            case e.ESC:
                me.clearValue();
                me.fireEvent("clear");
                break;
            case e.ENTER:
                var keyNav = me.getPicker().getNavigationModel();
                keyNav.selectHighlighted(e);
                break;
        }
    },

    setValue: function(value, doSelect) {
        var me = this,
            vm;
        if(typeof value === "string" || typeof value === "number") {
            if(value === "") {
                me.clearValue();
                return;
            }
            Ext.Ajax.request({
                url: me.restUrl,
                method: "GET",
                scope: me,
                params: {
                    id: value
                },
                success: function (response) {
                    var data = Ext.decode(response.responseText);
                    if (data.length === 1) {
                        vm = me.store.getModel().create(data[0]);
                        me.setValue(vm);
                        if(doSelect) {
                            me.fireEvent("select", me, vm, {});
                        }
                    }
                }
            });
        } else {
            me.callParent([value]);
        }
    }
});
