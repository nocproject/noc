//---------------------------------------------------------------------
// inv.interface LAG Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.interface.LAGPanel");

Ext.define("NOC.inv.interface.LAGPanel", {
    extend: "Ext.panel.Panel",
    uses: [],
    title: "LAG",
    closable: false,
    layout: "fit",
    rowClassField: "row_class",

    initComponent: function() {
        var me = this;

        Ext.apply(me, {
            items: [
                {
                    xtype: "gridpanel",
                    border: false,
                    autoScroll: true,
                    stateful: true,
                    stateId: "inv.interface-LAG-grid",
                    store: me.store,
                    columns: [
                        {
                            text: "Name",
                            dataIndex: "name"
                        },
                        {
                            text: "Count",
                            dataIndex: "count"
                        },
                        {
                            text: "Members",
                            dataIndex: "members"
                        },
                        {
                            text: "Profile",
                            dataIndex: "profile",
                            renderer: NOC.render.ClickableLookup("profile"),
                            onClick: me.onChangeProfile
                        },
                        {
                            text: "Description",
                            dataIndex: "description",
                            flex: 1
                        }
                    ],
                    viewConfig: {
                        getRowClass: Ext.bind(me.getRowClass, me),
                        listeners: {
                            scope: me,
                            cellclick: me.onCellClick
                        }
                    }
                }
            ]
        });
        me.callParent();
    },
    //
    onCellClick: function(view, cell, cellIndex, record, row,
                          rowIndex, e) {
        var me = this;
        if(e.target.tagName == "A") {
            var header = view.panel.headerCt.getHeaderAtIndex(cellIndex);
            if(header.onClick) {
                header.onClick.apply(me, [record]);
            }
        }
    },
    //
    onChangeProfile: function(record) {
        var me = this;
        Ext.create("NOC.inv.interface.ChangeInterfaceProfileForm", {
            app: me,
            record: record
        });
    },
    // Return Grid's row classes
    getRowClass: function(record, index, params, store) {
        var me = this;
        if(me.rowClassField) {
            var c = record.get(me.rowClassField);
            if(c) {
                return c;
            } else {
                return "";
            }
        } else {
            return "";
        }
    }
});
