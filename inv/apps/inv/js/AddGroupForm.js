//---------------------------------------------------------------------
// inv.inv AddGroupForm
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.AddGroupForm");

Ext.define("NOC.inv.inv.AddGroupForm", {
    extend: "Ext.window.Window",
    requires: ["NOC.inv.objectmodel.ContainerLookupField"],
    modal: true,
    autoShow: true,
    closeable: true,
    title: "Add Group",
    groupContainer: null,
    app: null,
    width: 400,

    initComponent: function() {
        var me = this;

        me.form = Ext.create("Ext.form.Panel", {
            bodyPadding: 4,
            layout: "anchor",
            defaults: {
                anchor: "100%",
                labelWidth: 40
            },
            items: [
                {
                    xtype: "textfield",
                    name: "name",
                    fieldLabel: "Name",
                    allowBlank: false
                },
                {
                    xtype: "inv.objectmodel.ContainerLookupField",
                    name: "type",
                    fieldLabel: "Type",
                    allowBlank: false
                }
            ],
            buttons: [
                {
                    text: "Close",
                    scope: me,
                    handler: me.onPressClose
                },
                {
                    text: "Add",
                    glyph: NOC.glyph.plus,
                    scope: me,
                    handler: me.onPressAdd
                }
            ]
        });

        Ext.apply(me, {
            items: [me.form]
        });
        me.callParent();
    },
    //
    onPressClose: function() {
        var me = this;
        me.close();
    },
    onPressAdd: function() {
        var me = this,
            values = me.form.getValues();
        Ext.Ajax.request({
            url: "/inv/inv/add_group/",
            method: "POST",
            jsonData: {
                name: values.name,
                type: values.type,
                container: me.groupContainer
            },
            scope: me,
            success: function() {
                me.close();
                me.app.store.reload();
            },
            failure: function() {
                NOC.error("Failed to save");
            }
        });
    }
});
