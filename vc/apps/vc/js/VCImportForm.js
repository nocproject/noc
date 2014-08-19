//---------------------------------------------------------------------
// VC Import form
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vc.VCImportForm");

Ext.define("NOC.vc.vc.VCImportForm", {
    extend: "Ext.Window",
    title: "Select VCs to import",
    autoShow: true,
    closable: false,
    modal: true,
    app: null,
    layout: "fit",
    closable: true,
    width: 600,
    height: 400,
    vc_domain: null,
    vc_filter: null,
    vc_filter_expression: null,

    initComponent: function() {
        var me = this;

        me.store = Ext.create("NOC.vc.vc.VCImportStore");
        Ext.apply(me, {
            items: [
                {
                    xtype: "gridpanel",
                    itemId: "grid",
                    store: me.store,
                    columns: [
                        {
                            header: "Label",
                            dataIndex: "label",
                            width: 50
                        },
                        {
                            header: "Name",
                            dataIndex: "name",
                            width: 200,
                            editor: "textfield",
                            renderer: NOC.render.htmlEncode
                        },
                        {
                            header: "Description",
                            dataIndex: "description",
                            flex: 1,
                            editor: "textfield",
                            renderer: NOC.render.htmlEncode
                        },
                        {
                            xtype: "glyphactioncolumn",
                            width: 25,
                            items: [
                                {
                                    glyph: NOC.glyph.times_circle_o,
                                    tooltip: "Delete",
                                    handler: function(grid, rowIndex, colIndex) {
                                        grid.getStore().removeAt(rowIndex);
                                    }
                                }
                            ]
                        }
                    ],
                    selType: "cellmodel",
                    plugins: [Ext.create("Ext.grid.plugin.CellEditing", {
                        clicksToEdit: 1
                    })],
                    dockedItems: [
                        {
                            xtype: "toolbar",
                            items: [
                                {
                                    text: "Save",
                                    glyph: NOC.glyph.save,
                                    scope: me,
                                    handler: me.onSave
                                }
                            ]
                        }
                    ]
                }
            ]
        });
        me.callParent();
        me.grid = me.getComponent("grid");
    },
    //
    onSave: function() {
        var me = this,
            items, data;

        items = me.grid.store.getRange().map(function(x) {
            return {
                l1: x.get("l1"),
                l2: x.get("l2"),
                name: x.get("name"),
                description: x.get("description")
            }
        });
        data = {
            vc_domain: me.vc_domain,
            items: items
        };
        // @todo: Display mask
        // Save
        Ext.Ajax.request({
            url: "/vc/vc/bulk/import/",
            method: "POST",
            scope: me,
            jsonData: data,
            success: function(response) {
                var r = Ext.decode(response.responseText);
                // @todo: Unmask
                this.close();
                Ext.Msg.show({
                    title: "Success!",
                    msg: Ext.String.format("{0} new VCs has been imported",
                                           r.imported),
                    buttons: Ext.Msg.OK
                });
                this.app.onImportSuccess();
            },
            failure: function() {
                // @todo: Unmask
                NOC.error("Failed to save VCs");
            }
        });
    },
    //
    getLabel: function(l1, l2) {
        if (l2)
            return l1.toString() + ", " + l2.toString();
        else
            return l1.toString();
    },
    // Compile VC Filter expression
    getFilter: function() {
        var me = this,
            expr = [];
        if(!me.vc_filter_expression) {
            expr = ["true"];
        } else {
            expr = me.vc_filter_expression.replace(/ /g, "").split(",").map(
                function(x) {
                    var m = x.match(/^(\d+)-(\d+)$/);
                    if(m) {
                        // a-b
                        return "(r.l1 >= " + m[1] + " && r.l1 <= " + m[2] + ")";
                    } else {
                        // a
                        return "(r.l1 == " + x + ")";
                    }
                }
            );
        }
        // Combine expression
        var src = "return " + expr.join(" || ") + ";"
        //
        return new Function("r", src);
    },
    // Load data to Grid
    loadData: function(data) {
        var me = this;
        // Get existing vlans
        Ext.Ajax.request({
            url: "/vc/vc/",
            method: "GET",
            params: {
                "vc_domain": me.vc_domain
            },
            scope: me,
            success: function(response) {
                var me = this,
                    filter = me.getFilter(),
                    r = Ext.decode(response.responseText);
                // Fill existing VC's map
                me.existing_vcs = {};
                Ext.each(r, function(x) {
                    me.existing_vcs[x.l1] = true;
                });
                // Left only new VCs
                var d = data.filter(function(x) {
                    return !me.existing_vcs[x.l1]
                });
                // Apply filters
                d = d.filter(filter);
                // Check new VCs found
                if(d.length == 0) {
                    NOC.info("No new VCs found");
                    me.close();
                } else {
                    // Load to store
                    me.store.loadData(d);
                }
            },
            failure: function() {
                NOC.error("Failed to get existing VC ids");
                me.close();
            }
        });
    },
    //
    // Load VLANs from get_vlans' result
    //
    loadVLANsFromSwitch: function(data) {
        var me = this;
        me.loadData(data.map(function(x) {
            return {
                label: me.getLabel(x.vlan_id, 0),
                l1: x.vlan_id,
                l2: 0,
                name: x.name,
                description: ""
            }
        }));
    }
});
