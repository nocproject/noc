//---------------------------------------------------------------------
// inv.networksegment application
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.networksegment.Application");

Ext.define("NOC.inv.networksegment.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.inv.networksegment.Model",
        "NOC.inv.networksegment.LookupField",
        "NOC.sa.managedobjectselector.LookupField",
        "Ext.ux.form.DictField"
    ],
    model: "NOC.inv.networksegment.Model",
    search: true,
    treeFilter: "parent",

    initComponent: function() {
        var me = this;

        me.ITEM_EFFECTIVE_SETTINGS = me.registerItem(
            "NOC.inv.networksegment.EffectiveSettingsPanel"
        );

        me.settingsButton = Ext.create("Ext.button.Button", {
            text: "Effective Settings",
            glyph: NOC.glyph.file,
            scope: me,
            handler: me.onEffectiveSettings
        });

        Ext.apply(me, {
            columns: [
                {
                    text: "Parent",
                    dataIndex: "parent",
                    width: 200,
                    renderer: NOC.render.Lookup("parent")
                },
                {
                    text: "Name",
                    dataIndex: "name",
                    width: 200
                },
                {
                    text: "Description",
                    dataIndex: "description",
                    flex: 1
                },
                {
                    text: "Selector",
                    dataIndex: "selector",
                    width: 100,
                    renderer: NOC.render.Lookup("selector")
                },
                {
                    text: "Obj.",
                    dataIndex: "count",
                    width: 30,
                    align: "right",
                    sortable: false
                }
            ],

            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: "Name",
                    uiStyle: "large",
                    allowBlank: false
                },
                {
                    name: "parent",
                    xtype: "inv.networksegment.LookupField",
                    fieldLabel: "Parent",
                    uiStyle: "large",
                    allowBlank: true
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: "Description",
                    uiStyle: "extra",
                    allowBlank: true
                },
                {
                    name: "settings",
                    xtype: "dictfield",
                    fieldLabel: "Settings"
                },
                {
                    name: "selector",
                    xtype: "sa.managedobjectselector.LookupField",
                    fieldLabel: "Selector",
                    allowBlank: true
                }
            ],

            formToolbar: [
                me.settingsButton
            ]
        });
        me.callParent();
    },
    //
    onEffectiveSettings: function() {
        var me = this;
        me.previewItem(me.ITEM_EFFECTIVE_SETTINGS, me.currentRecord);
    }
});
