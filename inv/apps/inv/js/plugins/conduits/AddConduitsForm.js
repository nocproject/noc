//---------------------------------------------------------------------
// inv.inv Add conduit form
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.conduits.AddConduitsForm");

Ext.define("NOC.inv.inv.plugins.conduits.AddConduitsForm", {
    extend: "Ext.Window",
    title: "Add Conduits",
    closable: true,
    layout: "fit",
    app: null,
    modal: true,
    width: 400,
    height: 130,
    storeData: null,

    initComponent: function() {
        var me = this;

        me.store = Ext.create("Ext.data.Store", {
            model: null,
            fields: ["id", "label"],
            data: me.storeData
        });

        me.formPanel = Ext.create("Ext.form.Panel", {
            items: [
                {
                    name: "connect_to",
                    xtype: "combobox",
                    fieldLabel: "Connect to",
                    allowBlank: false,
                    store: me.store,
                    displayField: "label",
                    valueField: "id",
                    anchor: "100%"
                },
                {
                    name: "project_distance",
                    xtype: "numberfield",
                    fieldLabel: "Project distance (m)",
                    allowBlank: true
                }
            ],
            buttons: [
                {
                    text: "Connect",
                    glyph: NOC.glyph.plus,
                    formBind: true,
                    scope: me,
                    handler: me.onConnect
                },
                {
                    text: "Close",
                    glyph: NOC.glyph.cross,
                    scope: me,
                    handler: me.onClose
                }
            ]
        });

        Ext.apply(me, {
            items: [me.formPanel]
        });

        me.callParent();
    },
    //
    onClose: function() {
        var me = this;
        me.close();
    },
    //
    onConnect: function() {
        var me = this,
            values = me.formPanel.getForm().getValues();
        Ext.Ajax.request({
            url: "/inv/inv/" + me.app.currentId + "/plugin/conduits/conduits/",
            method: "POST",
            jsonData: values,
            scope: me,
            success: function() {
                me.app.reload();
                me.close();
            },
            failure: function() {
                NOC.error("Failed to create conduits");
            }
        });
    }
});
