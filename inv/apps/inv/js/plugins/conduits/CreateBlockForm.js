//---------------------------------------------------------------------
// inv.inv Create block Form
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.conduits.CreateBlockForm");

Ext.define("NOC.inv.inv.plugins.conduits.CreateBlockForm", {
    extend: "Ext.Window",
    title: "Create Block",
    closable: true,
    layout: "fit",
    app: null,
    modal: true,
    width: 300,
    height: 200,

    initComponent: function() {
        var me = this;
        me.formPanel = Ext.create("Ext.form.Panel", {
            items: [
                {
                    name: "count",
                    xtype: "numberfield",
                    fieldLabel: "Count",
                    allowBlank: false,
                    minValue: 1,
                    value: 1
                },
                {
                    name: "w",
                    xtype: "numberfield",
                    fieldLabel: "Columns",
                    allowBlank: false,
                    minValue: 1,
                    value: 1
                },
                {
                    name: "d",
                    xtype: "numberfield",
                    fieldLabel: "Diameter (mm)",
                    value: 100,
                    allowBlank: false,
                    minValue: 1
                },
                {
                    name: "start",
                    xtype: "numberfield",
                    fieldLabel: "First Number",
                    value: 1,
                    allowBlank: false,
                    minValue: 1
                }
            ],
            buttons: [
                {
                    text: "Create",
                    glyph: NOC.glyph.plus,
                    formBind: true,
                    scope: me,
                    handler: me.onCreateBlock
                },
                {
                    text: "Close",
                    glyph: NOC.glyph.cross,
                    scope: me,
                    handler: me.onClose
                }
            ]

        });
        //
        Ext.apply(me, {
            items: [me.formPanel]
        });
        //
        me.callParent();
    },
    //
    onClose: function() {
        var me = this;
        me.close();
    },
    //
    onCreateBlock: function() {
        var me = this,
            values = me.formPanel.getForm().getValues();
        me.app.createBlock(values);
        me.close();
    }
});