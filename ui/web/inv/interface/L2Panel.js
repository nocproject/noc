//---------------------------------------------------------------------
// inv.interface L2 Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.interface.L2Panel");

Ext.define("NOC.inv.interface.L2Panel", {
    extend: "Ext.panel.Panel",
    requires: [
        "Ext.ux.grid.column.GlyphAction"
    ],
    title: __("Switchports"),
    closable: false,

    initComponent: function() {
        var me = this;

        Ext.apply(me, {
            items: [
                {
                    xtype: "gridpanel",
                    border: false,
                    autoScroll: true,
                    stateful: true,
                    stateId: "inv.interface-L2-grid",
                    store: me.store,
                    columns: [
                        {
                            xtype: "glyphactioncolumn",
                            width: 25,
                            items: [
                                {
                                    tooltip: __("Show MACs"),
                                    glyph: NOC.glyph.play,
                                    scope: me,
                                    handler: me.showMAC,
                                    disabled: !me.app.hasPermission("get_mac")
                                }
                            ]
                        },
                        {
                            text: __("Name"),
                            dataIndex: "name"
                        },
                        {
                            text: __("Untag."),
                            dataIndex: "untagged_vlan",
                            width: 50
                        },
                        {
                            text: __("Tagged"),
                            dataIndex: "tagged_vlans",
                            hidden: true
                        },
                        {
                            text: __("Tagged (Ranges)"),
                            dataIndex: "tagged_range"
                        },
                        {
                            text: __("Description"),
                            dataIndex: "description",
                            flex: 1
                        }
                    ]
                }
            ]
        });
        me.callParent();
    },
    //
    showMAC: function(grid, rowIndex, colIndex, item, event, record) {
        var me = this;

        me.currentMAC = record;
        NOC.mrt({
            scope: me,
            params: [
                {
                    id: me.app.currentObject,
                    script: "get_mac_address_table",
                    args: {
                        interface: record.get("name")
                    }
                }
            ],
            errorMsg: __("Failed to get MACs"),
            cb: me.showMACForm
        });
    },
    //
    showMACForm: function(data, scope) {
        Ext.create("NOC.inv.interface.MACForm", {
            objectId: scope.app.currentObject,
            data: data,
            name: scope.currentMAC.get("name"),
            title: Ext.String.format("MACs on {0}",
                scope.currentMAC.get("name"))
        });
    }
});
