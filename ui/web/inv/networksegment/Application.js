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
        "NOC.inv.networksegment.TreeCombo",
        "NOC.sa.managedobjectselector.LookupField",
        "Ext.ux.form.DictField"
    ],
    model: "NOC.inv.networksegment.Model",
    search: true,

    initComponent: function() {
        var me = this;

        me.ITEM_EFFECTIVE_SETTINGS = me.registerItem(
            "NOC.inv.networksegment.EffectiveSettingsPanel"
        );

        me.settingsButton = Ext.create("Ext.button.Button", {
            text: __("Effective Settings"),
            glyph: NOC.glyph.file,
            scope: me,
            handler: me.onEffectiveSettings
        });

        me.showMapButton = Ext.create("Ext.button.Button", {
            text: __("Show Map"),
            glyph: NOC.glyph.globe,
            scope: me,
            handler: me.onShowMap
        });

        Ext.apply(me, {
            columns: [
                {
                    text: __("Parent"),
                    dataIndex: "parent",
                    width: 200,
                    renderer: NOC.render.Lookup("parent"),
                    hidden: true
                },
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 200
                },
                {
                    text: __("Description"),
                    dataIndex: "description",
                    flex: 1
                },
                {
                    text: __("Tags"),
                    dataIndex: "tags",
                    width: 100,
                    renderer: NOC.render.Tags
                },
                {
                    text: __("Selector"),
                    dataIndex: "selector",
                    width: 100,
                    renderer: NOC.render.Lookup("selector")
                },
                {
                    text: __("Redundant"),
                    dataIndex: "is_redundant",
                    width: 50,
                    renderer: NOC.render.Lookup("is_redundant")
                },
                {
                    text: __("Obj."),
                    dataIndex: "count",
                    width: 30,
                    align: "right",
                    sortable: false,
                    renderer: NOC.render.Badge
                },
                {
                    text: __("Max Links"),
                    dataIndex: "max_shown_downlinks",
                    width: 70
                }
            ],

            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    uiStyle: "large",
                    allowBlank: false
                },
                Ext.create('NOC.inv.networksegment.TreeCombo', {
                    name: "parent",
                    emptyText: __("Select parent..."),
                    fieldLabel: __("Parent"),
                    listWidth: 0.6,
                    labelAlign: "left",
                    labelWidth: 100,
                    margin: '0 0 5',
                    allowBlank: true
                }),
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    uiStyle: "extra",
                    allowBlank: true
                },
                Ext.create('NOC.inv.networksegment.TreeCombo', {
                    name: "sibling",
                    emptyText: __("Select sibling..."),
                    fieldLabel: __("Sibling"),
                    listWidth: 0.6,
                    labelAlign: "left",
                    labelWidth: 100,
                    margin: '0 0 5',
                    allowBlank: true
                }),
                {
                    name: "settings",
                    xtype: "dictfield",
                    fieldLabel: __("Settings")
                },
                {
                    name: "selector",
                    xtype: "sa.managedobjectselector.LookupField",
                    fieldLabel: __("Selector"),
                    allowBlank: true
                },
                {
                    name: "max_shown_downlinks",
                    xtype: "numberfield",
                    fieldLabel: __("Max Links"),
                    allowBlank: true
                },
                {
                    name: "tags",
                    xtype: "tagsfield",
                    fieldLabel: __("Tags"),
                    allowBlank: true
                }
            ],

            formToolbar: [
                me.settingsButton,
                me.showMapButton
            ]
        });
        me.callParent();
    },
    //
    onEffectiveSettings: function() {
        var me = this;
        me.previewItem(me.ITEM_EFFECTIVE_SETTINGS, me.currentRecord);
    },
    //
    onShowMap: function() {
        var me = this;
        NOC.launch("inv.map", "history", {
            args: [me.currentRecord.get("id")]
        });
    },
    filters: [
        {
            title: __("By Segment"),
            name: "parent",
            ftype: "tree",
            lookup: "inv.networksegment"
        }
    ],
    levelFilter: {
        icon: NOC.glyph.level_down,
        color: NOC.colors.level_down,
        filter: 'parent',
        tooltip: __('Parent filter')
    }
});
