//---------------------------------------------------------------------
// inv.configuredmap application
//---------------------------------------------------------------------
// Copyright (C) 2007-2022 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.configuredmap.Application");

Ext.define("NOC.inv.configuredmap.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "Ext.ux.form.GridField",
        "Ext.ux.form.StringsField",
        "NOC.core.label.LabelField",
        "NOC.core.tagfield.Tagfield",
        "NOC.core.JSONPreview",
        "NOC.core.ListFormField",
        "NOC.inv.configuredmap.Model",
        "NOC.core.combotree.ComboTree",
        "NOC.sa.managedobject.LookupField",
        "NOC.core.ComboBox",
        "NOC.main.imagestore.LookupField",
        "NOC.main.ref.stencil.LookupField",
        "NOC.inv.configuredmap.NodeLookupField"
    ],
    model: "NOC.inv.configuredmap.Model",
    search: true,

    initComponent: function() {
        var me = this;

        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: new Ext.XTemplate('/inv/configuredmap/{id}/json/'),
            previewName: new Ext.XTemplate('Spec: {name}')
        });

        me.ITEM_JSON = me.registerItem(me.jsonPanel);

        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 150
                },
            ],

            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false,
                    uiStyle: "large"
                },
                {
                    xtype: "tabpanel",
                    layout: "fit",
                    autoScroll: true,
                    tabPosition: "left",
                    tabBar: {
                        tabRotation: 0,
                        layout: {
                            align: "stretch"
                        }
                    },
                    anchor: "-0, -50",
                    defaults: {
                        autoScroll: true,
                        layout: "anchor",
                        textAlign: "left",
                        padding: 10
                    },
                    items: [
                        {
                            title: __("Common"),
                            items: [
                                {
                                    name: "layout",
                                    xtype: "combobox",
                                    fieldLabel: __("Layout"),
                                    allowBlank: false,
                                    uiStyle: "medium",
                                    store: [
                                        ["auto", "auto"],
                                        ["manual", "manual"],
                                        ["spring", "spring"],
                                        ["radial", "radial"]
                                    ]
                                },
                                {
                                    xtype: "fieldset",
                                    title: __("Map settings"),
                                    layout: "hbox",
                                    defaults: {
                                        padding: 4
                                    },
                                    items: [
                                        {
                                            name: "width",
                                            xtype: "numberfield",
                                            fieldLabel: __("Width"),
                                            allowBlank: true,
                                            minValue: 1,
                                            uiStyle: "small"
                                        },
                                        {
                                            name: "height",
                                            xtype: "numberfield",
                                            fieldLabel: __("Height"),
                                            allowBlank: true,
                                            minValue: 1,
                                            uiStyle: "small"
                                        },
                                        {
                                            name: "background_image",
                                            xtype: "main.imagestore.LookupField",
                                            fieldLabel: __("Background Image"),
                                            allowBlank: true
                                        }
                                    ]
                                },
                                {
                                    name: "add_linked_node",
                                    xtype: "checkboxfield",
                                    boxLabel: __("Add Linked Nodes"),
                                    tooltip: __("If check - use Credential Check Rules (Service Activation -> Setup -> Credential Check Rules)<br/>" +
                                        " for suggest credential"),
                                    allowBlank: true,
                                    listeners: {
                                        render: me.addTooltip
                                    }
                                },
                                {
                                    name: "enable_node_portal",
                                    xtype: "checkboxfield",
                                    boxLabel: __("Enable Node Portal"),
                                    tooltip: __("If check - use Credential Check Rules (Service Activation -> Setup -> Credential Check Rules)<br/>" +
                                        " for suggest credential"),
                                    allowBlank: true,
                                    listeners: {
                                        render: me.addTooltip
                                    }
                                }
                            ]
                        },
                        {
                            title: __("Nodes"),
                            items: [
                                {
                                    name: "nodes",
                                    xtype: "listform",
                                    labelAlign: "top",
                                    rows: 10,
                                    items: [
                                        {
                                            name: "node_type",
                                            xtype: "combobox",
                                            fieldLabel: __("Type"),
                                            allowBlank: false,
                                            uiStyle: "medium",
                                            store: [
                                                ["group", "group"],
                                                ["segment", "segment"],
                                                ["managedobject", "managedobject"],
                                                ["other", "other"]
                                            ]
                                        },
                                        {
                                            xtype: "fieldset",
                                            title: __("Reference"),
                                            layout: "hbox",
                                            defaults: {
                                                padding: 4
                                            },
                                            items: [
                                                {
                                                    name: "resource_group",
                                                    xtype: "noc.core.combotree",
                                                    restUrl: "/inv/resourcegroup/",
                                                    fieldLabel: __("Resource Group"),
                                                    listWidth: 1,
                                                    listAlign: 'left',
                                                    labelAlign: "top",
                                                    width: 300
                                                },
                                                {
                                                    xtype: "noc.core.combotree",
                                                    restUrl: "/inv/networksegment/",
                                                    name: "segment",
                                                    fieldLabel: __("Segment"),
                                                    allowBlank: true,
                                                    labelAlign: "top",
                                                    width: 200,
                                                },
                                                {
                                                    name: "managed_object",
                                                    xtype: "sa.managedobject.LookupField",
                                                    fieldLabel: __("Managed Object"),
                                                    allowBlank: true,
                                                    labelAlign: "top",
                                                    width: 200,
                                                },
                                                {
                                                    name: "add_nested",
                                                    xtype: "checkbox",
                                                    boxLabel: __("Add nested nodes"),
                                                    tooltip: __("Display check state on Object Form"),
                                                    allowBlank: true,
                                                    listeners: {
                                                        render: me.addTooltip
                                                    }
                                                }
                                            ]
                                        },
                                        {
                                            xtype: "fieldset",
                                            title: __("Shape"),
                                            layout: "hbox",
                                            defaults: {
                                                padding: 4
                                            },
                                            items: [
                                                {
                                                    name: "shape",
                                                    xtype: "combobox",
                                                    fieldLabel: __("Type"),
                                                    labelAlign: "top",
                                                    allowBlank: true,
                                                    width: 50,
                                                    uiStyle: "medium",
                                                    store: [
                                                        ["stencil", "stencil"],
                                                        ["rectangle", "rectangle"],
                                                        ["ellipse", "ellipse"]
                                                    ]
                                                },
                                                {
                                                    name: "stencil",
                                                    xtype: "main.ref.stencil.LookupField",
                                                    fieldLabel: __("Shape"),
                                                    labelAlign: "top",
                                                    width: 100,
                                                    allowBlank: true
                                                },
                                                {
                                                    name: "title",
                                                    xtype: "textfield",
                                                    fieldLabel: __("Title"),
                                                    labelAlign: "top",
                                                    allowBlank: true,
                                                    width: 200,
                                                    uiStyle: "large"
                                                }
                                            ]
                                        }
                                    ]
                                },
                            ]
                        },
                        {
                            title: __("Links"),
                            items: [
                                {
                                    name: "links",
                                    xtype: "listform",
                                    labelAlign: "top",
                                    rows: 10,
                                    items: [
                                        {
                                            xtype: "core.tagfield",
                                            url: "/inv/configuredmap/" + me.currentId + "/nodes/",
                                            fieldLabel: __("Target Nodes"),
                                            tooltip: __("Metric Type inputs to Expression"),
                                            name: "target_node",
                                            labelWidth: 150,
                                            width: 300,
                                            listeners: {
                                                render: me.addTooltip
                                            }
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ],
            formToolbar: [
                {
                    text: __("JSON"),
                    glyph: NOC.glyph.file,
                    tooltip: __("Show JSON"),
                    hasAccess: NOC.hasPermission("read"),
                    scope: me,
                    handler: me.onJSON
                }
            ]
        });
        me.callParent();
    },

    onJSON: function() {
        var me = this;
        me.showItem(me.ITEM_JSON);
        me.jsonPanel.preview(me.currentRecord);
    }
});
