//---------------------------------------------------------------------
// inv.interface L2 Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.interface.L2Panel");

Ext.define("NOC.inv.interface.L2Panel", {
    extend: "Ext.panel.Panel",
    title: __("Switchports"),
    closable: false,
    layout: "fit",

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
    showMAC: function(grid, rowIndex, colIndex) {
        var me = this,
            r = me.store.getAt(rowIndex);

        me.currentMAC = r;
        NOC.mrt({
            url: "/inv/interface/mrt/get_mac/",
            selector: me.app.currentObject,
            mapParams: {
                interface: r.get("name")
            },
            loadMask: me,
            scope: me,
            success: me.showMACForm,
            failure: function() {
                NOC.error(__("Failed to get MACs"));
            }
        });
    },
    //
    showMACForm: function(result) {
        var me = this,
            r = result[0];
        if(r.status) {
            Ext.create("NOC.inv.interface.MACForm", {
                data: r.result,
                title: Ext.String.format("MACs on {0}",
                    me.currentMAC.get("name"))
            });
        } else {
            NOC.error(__("Failed to get MACs"));
        }
    }
});
