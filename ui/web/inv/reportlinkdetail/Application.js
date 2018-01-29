//---------------------------------------------------------------------
// inv.reportllinkdetail application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.reportlinkdetail.Application");

Ext.define("NOC.inv.reportlinkdetail.Application", {
    extend: "NOC.core.Application",
    requires: [
        "NOC.inv.networksegment.TreeCombo",
        "NOC.sa.administrativedomain.TreeCombo",
        "NOC.sa.managedobjectselector.LookupField"
    ],

    initComponent: function() {
        var me = this;

        me.columnsStore = Ext.create("Ext.data.Store", {
            fields: ["id", "label", {
                name: "is_active",
                type: "boolean"
            }],
            data: [
                ["admin_domain", __("Admin. Domain"), true],
                ["object1_name", __("Object1 Name"), true],
                ["object1_address", __("IP1"), true],
                ["object1_iface", __("Interface1"), true],
                ["object2_name", __("Object2 Name"), true],
                ["object2_address", __("IP2"), true],
                ["object2_iface", __("Interface2"), true],
                ["link_proto", __("Link Proto"), true],
                ["last_seen", __("Link Last Seen"), false]
                // ["id", __("ID"), false],
                // ["object_name", __("Object Name"), true],
                // ["object_address", __("IP"), true],
                // ["object_status", __("Object Status"), true],
                // ["profile_name", __("Profile"), true],
                // ["object_profile", __("Object Profile"), false],
                // ["object_vendor", __("Vendor"), false],
                // ["object_platform", __("Platform"), false],
                // ["object_version", __("SW Version"), false],
                // ["object_serial", __("Serial Number"), false],
                // ["avail", __("Avail"), false],
                // ["admin_domain", __("Admin. Domain"), true],
                // ["container", __("Container"), false],
                // ["segment", __("Segment"), true],
                // ["phys_interface_count", __("Physical Iface Count"), false],
                // ["link_count", __("Link Count"), false],
                // ["discovery_problem", __("Discovery Problem"), false],
                // ["interface_type_count", __("Interface count by type"), false],
                // ["object_caps", __("Object capabilities"), false],
                // ["object_tags", __("Object Tags"), false],
                // ["sorted_tags", __("Sorted Tags"), false]
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
        me.segment = null;
        me.selector = null;

        me.formPanel = Ext.create("Ext.form.Panel", {
            autoScroll: true,
            defaults: {
                labelWidth: 60
            },
            items: [
                {
                    name: "segment",
                    xtype: "inv.networksegment.TreeCombo",
                    fieldLabel: __("Segment"),
                    listWidth: 1,
                    listAlign: 'left',
                    labelAlign: "left",
                    width: 500,
                    listeners: {
                        scope: me,
                        select: function(combo, record) {
                            me.segment = record.get("id")
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
            "/inv/reportlinkdetail/download/?o_format=" + format
        ];

        if(me.adm_domain) {
            url.push("&administrative_domain=" + me.adm_domain);
        }

        if(me.segment) {
            url.push("&segment=" + me.segment);
        }

        if(me.selector) {
            url.push("&selector=" + me.selector);
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
