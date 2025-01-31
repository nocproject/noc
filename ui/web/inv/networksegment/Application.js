//---------------------------------------------------------------------
// inv.networksegment application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.networksegment.Application");

Ext.define("NOC.inv.networksegment.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.core.label.LabelField",
        "NOC.inv.allocationgroup.LookupField",
        "NOC.inv.networksegment.Model",
        "NOC.inv.networksegment.TreeCombo",
        "NOC.inv.networksegment.EffectiveSettingsPanel",
        "NOC.inv.networksegmentprofile.LookupField",
        "NOC.main.remotesystem.LookupField",
        "NOC.vc.vlanfilter.LookupField",
        "NOC.vc.l2domain.LookupField",
        "NOC.vc.vlan.LookupField",
        "Ext.ux.form.DictField",
        "Ext.ux.form.GridField"
    ],
    model: "NOC.inv.networksegment.Model",
    rowClassField: "row_class",
    search: true,
    helpId: "reference-network-segment",

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

        me.cardButton = Ext.create("Ext.button.Button", {
            text: __("Card"),
            glyph: NOC.glyph.eye,
            scope: me,
            handler: me.onCard
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
                    text: __("Labels"),
                    dataIndex: "labels",
                    width: 100,
                    renderer: NOC.render.LabelField
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
                },
                {
                    text: __("Max Objects"),
                    dataIndex: "max_objects",
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
                    name: "profile",
                    xtype: "inv.networksegmentprofile.LookupField",
                    fieldLabel: __("Profile"),
                    allowBlank: false
                },
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
                    name: "max_shown_downlinks",
                    xtype: "numberfield",
                    fieldLabel: __("Max Links"),
                    allowBlank: true,
                    uiStyle: "medium"
                },
                {
                    name: "max_objects",
                    xtype: "numberfield",
                    fieldLabel: __("Max Objects"),
                    allowBlank: true,
                    uiStyle: "medium"
                },
                {
                    name: "horizontal_transit_policy",
                    xtype: "combobox",
                    fieldLabel: __("Horizontal Transit Policy"),
                    allowBlank: false,
                    store: [
                        ["E", __("Always Enable")],
                        ["C", __("Calculate")],
                        ["D", __("Disable")],
                        ["P", __("Profile")]
                    ],
                    uiStyle: "medium"
                },
                {
                    name: "enable_horizontal_transit",
                    xtype: "checkbox",
                    boxLabel: __("Enable Horizontal Transit")
                },
                {
                    name: "vlan_border",
                    xtype: "checkbox",
                    boxLabel: __("VLAN Border")
                },
                {
                    name: "allocation_group",
                    xtype: "inv.allocationgroup.LookupField",
                    fieldLabel: __("Allocation Group"),
                    allowBlank: true
                },
                {
                    name: "l2_domain",
                    xtype: "vc.l2domain.LookupField",
                    fieldLabel: __("L2 Domain"),
                    allowBlank: true
                },
                {
                    name: "vlan_translation",
                    fieldLabel: __("VLAN Translation"),
                    xtype: "gridfield",
                    allowBlank: true,
                    columns: [
                        {
                            text: __("Filter"),
                            dataIndex: "filter",
                            width: 300,
                            renderer: NOC.render.Lookup("filter"),
                            editor: "vc.vlanfilter.LookupField"
                        },
                        {
                            text: __("Rule"),
                            dataIndex: "rule",
                            width: 100,
                            editor: {
                                xtype: "combobox",
                                store: [
                                    ["map", "map"],
                                    ["push", "push"]
                                ]
                            }
                        },
                        {
                            text: __("Parent VLAN"),
                            dataIndex: "parent_vlan",
                            flex: 1,
                            editor: "vc.vlan.LookupField",
                            renderer: NOC.render.Lookup("parent_vlan")
                        }
                    ]
                },
                {
                    name: "l2_mtu",
                    xtype: "numberfield",
                    fieldLabel: __("L2 MTU"),
                    allowBlank: true
                },
                {
                    xtype: "fieldset",
                    layout: "hbox",
                    title: __("Integration"),
                    defaults: {
                        padding: 4,
                        labelAlign: "top"
                    },
                    items: [
                        {
                            name: "remote_system",
                            xtype: "main.remotesystem.LookupField",
                            fieldLabel: __("Remote System"),
                            allowBlank: true
                        },
                        {
                            name: "remote_id",
                            xtype: "textfield",
                            fieldLabel: __("Remote ID"),
                            allowBlank: true,
                            uiStyle: "medium"
                        },
                        {
                            name: "bi_id",
                            xtype: "displayfield",
                            fieldLabel: __("BI ID"),
                            allowBlank: true,
                            uiStyle: "medium"
                        }
                    ]
                },
                {
                    name: "labels",
                    xtype: "labelfield",
                    fieldLabel: __("Labels"),
                    allowBlank: true,
                    query: {
                        "enable_networksegment": true
                    },
                }
            ],

            formToolbar: [
                me.settingsButton,
                me.showMapButton,
                me.cardButton
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
            args: ["segment", me.currentRecord.get("id")]
        });
    },
    //
    onCard: function () {
        var me = this;
        if (me.currentRecord) {
            window.open(
                "/api/card/view/segment/" + me.currentRecord.get("id") + "/"
            );
        }
    },
    filters: [
        {
            title: __("By Segment"),
            name: "parent",
            ftype: "tree",
            lookup: "inv.networksegment"
        },
        {
            title: __("By Profile"),
            name: "profile",
            ftype: "lookup",
            lookup: "inv.networksegmentprofile"
        }
    ],
    levelFilter: {
        icon: NOC.glyph.level_down,
        color: NOC.colors.level_down,
        filter: 'parent',
        tooltip: __('Parent filter')
    }
});
