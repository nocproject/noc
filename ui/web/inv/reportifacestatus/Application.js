//---------------------------------------------------------------------
// inv.reportifacestatus application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.reportifacestatus.Application");

Ext.define("NOC.inv.reportifacestatus.Application", {
    extend: "NOC.core.Application",
    requires: [
        "NOC.sa.administrativedomain.TreeCombo",
        "NOC.sa.managedobjectselector.LookupField",
        "NOC.inv.interfaceprofile.LookupField"
    ],

    initComponent: function() {
        var me = this;

        me.columnsStore = Ext.create("Ext.data.Store", {
            fields: ["id", "label", {
                name: "is_active",
                type: "boolean"
            }],
            data: [
                ["object_name", __("Object Name"), true],
                ["object_address", __("IP address"), true],
                ["object_model", __("Object Model"), true],
                ["object_software", __("Object Software"), true],
                ["object_port_name", __("Port name"), true],
                ["object_port_profile_name", __("Port profile name"), true],
                ["object_port_status", __("Port status"), true],
                ["object_link_status", __("Link status"), true],
                ["object_port_speed", __("Port speed"), true],
                ["object_port_duplex", __("Port duplex"), true]
            ]
        });

         me.columnsGrid = Ext.create("Ext.grid.Panel", {
            store: me.columnsStore,
            autoScroll: true,
            columns: [
                {
                    text: __("Active"),
                    dataIndex: "is_active",
                    width: 25,
                    renderer: NOC.render.Bool,
                    editor: "checkbox"
                },
                {
                    text: __("Field"),
                    dataIndex: "label",
                    flex: 1
                }
            ],
            selModel: "cellmodel",
            plugins: [
                {
                    ptype: "cellediting",
                    clicksToEdit: 1
                }
            ],
            viewConfig: {
                plugins: {
                    ptype: 'gridviewdragdrop',
                    dragText: 'Drag and drop to reorganize'
                }
            }
        });

        me.formatButton = Ext.create("Ext.button.Segmented", {
            items: [
                {
                    text: __("CSV"),
                    width: 70
                },
                {
                    text: __("Excel"),
                    pressed: true,
                    width: 70
                }
            ],
            anchor: null
        });

        me.adm_domain = null;
        me.iprofile = null;
        me.selector = null;

        me.formPanel = Ext.create("Ext.form.Panel", {
            autoScroll: true,
            defaults: {
                labelWidth: 150
            },
            items: [
                {
                    name: "interface_profile",
                    xtype: "inv.interfaceprofile.LookupField",
                    fieldLabel: __("By Interface Profile"),
                    listWidth: 1,
                    listAlign: 'left',
                    labelAlign: "left",
                    width: 500,
                    listeners: {
                        scope: me,
                        select: function(combo, record) {
                            me.iprofile = record.get("id")
                        }
                    }
                },
                {
                    name: "administrative_domain",
                    xtype: "sa.administrativedomain.TreeCombo",
                    fieldLabel: __("By Adm. domain"),
                    listWidth: 1,
                    listAlign: 'left',
                    labelAlign: "left",
                    width: 500,
                    allowBlank: true,
                    listeners: {
                        scope: me,
                        select: function(combo, record) {
                            me.adm_domain = record.get("id")
                        }
                    }
                },
                {
                    name: "Selector",
                    xtype: "sa.managedobjectselector.LookupField",
                    fieldLabel: __("By Selector"),
                    listWidth: 1,
                    listAlign: 'left',
                    labelAlign: "left",
                    width: 500,
                    allowBlank: true,
                    listeners: {
                        scope: me,
                        select: function(combo, record) {
                            me.selector = record.get("id")
                        }
                    }
                },
                {
                    name: "zero",
                    xtype: "checkboxfield",
                    boxLabel: __("Exclude ports in the status down"),
                    value: true,
                    allowBlank: false
                },
                {
                    name: "def_profile",
                    xtype: "checkboxfield",
                    boxLabel: __("Exclude interfaces with the \"default\" name profile " +
                        "(for Selector and Administrative Domain filter)"),
                    value: true,
                    allowBlank: false
                },
                me.formatButton,
                me.columnsGrid
            ],
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        {
                            text: __("Download"),
                            glyph: NOC.glyph.download,
                            scope: me,
                            handler: me.onDownload,
                            formBind: true
                        }
                    ]
                }
            ]
        });
        Ext.apply(me, {
            items: [me.formPanel]
        });
        me.callParent();
    },

    onDownload: function() {
        var me = this,
            v = me.formPanel.getValues(),
            format = "csv",
            url,
            columns = [];

        if(me.formatButton.items.items[1].pressed) {
            format = "xlsx"
        }

        url = [
            "/inv/reportifacestatus/download/?o_format=" + format
        ];

        if(me.adm_domain) {
            url.push("&administrative_domain=" + me.adm_domain);
        }

        if(me.iprofile) {
            url.push("&interface_profile=" + me.iprofile);
        }

        if(me.selector) {
            url.push("&selector=" + me.selector);
        }

        if(v.zero) {
            url.push("&zero=" + v.zero);
        }

        if(v.def_profile) {
            url.push("&def_profile=" + v.def_profile);
        }

        me.columnsStore.each(function(record) {
            if(record.get("is_active")) {
                columns.push(record.get("id"));
            }
        });

        url.push("&columns=" + columns.join(","));

        window.open(url.join(""));
    }
});
