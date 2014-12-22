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
    fromTitle: "Available",
    toTitle: "Selected",
    buttons: ["add", "remove"],
    buttonsGlyph: {
        add: NOC.glyph.arrow_right,
        remove: NOC.glyph.arrow_left
    },

    initComponent: function() {
        var me = this,
            sclass = me.$className.replace("M2MField", "Lookup");
        Ext.apply(me, {
            store: Ext.create(sclass, {
                autoLoad: true
            })
        });
        me.callParent();
    },

    createButtons: function() {
        var me = this,
            buttons = [];

        if (!me.hideNavIcons) {
            Ext.Array.forEach(me.buttons, function(name) {
                buttons.push({
                    xtype: "button",
                    tooltip: me.buttonsText[name],
                    handler: me["on" + Ext.String.capitalize(name) + "BtnClick"],
                    glyph: me.buttonsGlyph[name],
                    navBtn: true,
                    scope: me,
                    margin: "4 0 0 0"
                });
            });
        }
        return buttons;
    },

    _setValue: function(value) {
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

        me.store.load({
            scope: me,
            callback: function(records, operation, success) {
                if(success) {
                    var fromStore = me.fromField.boundList.getStore(),
                        toStore = me.toField.boundList.getStore();
                    fromStore.removeAll();
                    toStore.removeAll();
                    fromStore.loadRecords(records);
                    // me.setRawValue(value);
                }
            }
        });
    }
});
