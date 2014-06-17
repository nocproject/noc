//---------------------------------------------------------------------
// VRF Import form
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.vrf.VRFImportForm");

Ext.define("NOC.ip.vrf.VRFImportForm", {
    extend: "Ext.Window",
    requires: [
        "NOC.ip.vrfgroup.LookupField"
    ],
    title: "Select VRFs to import",
    autoShow: true,
    modal: true,
    app: null,
    layout: "fit",
    closable: true,
    width: 600,
    height: 400,

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            store: Ext.create("NOC.ip.vrf.VRFImportStore"),
            items: [
                {
                    xtype: "gridpanel",
                    itemId: "grid",
                    columns: [
                        {
                            header: "Name",
                            dataIndex: "name",
                            editor: "textfield"
                        },
                        {
                            header: "RD",
                            dataIndex: "rd",
                            editor: "textfield",
                            width: 100
                        },
                        {
                            header: "Group",
                            dataIndex: "vrf_group",
                            editor: "ip.vrfgroup.LookupField",
                            renderer: NOC.render.Lookup("vrf_group")
                        },
                        {
                            header: "IPv4",
                            dataIndex: "afi_ipv4",
                            renderer: NOC.render.Bool,
                            editor: "checkboxfield",
                            width: 30
                        },
                        {
                            header: "IPv6",
                            dataIndex: "afi_ipv6",
                            renderer: NOC.render.Bool,
                            editor: "checkboxfield",
                            width: 30
                        },
                        {
                            header: "Description",
                            dataIndex: "description",
                            flex: 1,
                            editor: "textfield"
                        },
                        {
                            xtype: "glyphactioncolumn",
                            width: 25,
                            items: [
                                {
                                    glyph: NOC.glyph.minus_circle,
                                    tooltip: "Delete",
                                    handler: function(grid, rowIndex, colIndex) {
                                        grid.getStore().removeAt(rowIndex);
                                    }
                                }
                            ]
                        }
                    ],
                    selType: "rowmodel",
                    plugins: [Ext.create("Ext.grid.plugin.RowEditing", {
                        clicksToEdit: 1,
                        listeners: {
                            edit: {
                                scope: me,
                                fn: me.onRowEdit
                            }
                        }
                    })],
                    listeners: {
                        validateedit: function(editor, e) {
                            // @todo: Bring to plugin
                            var form = editor.editor.getForm();
                            // Process comboboxes
                            form.getFields().each(function(field) {
                                e.record.set(field.name, field.getValue());
                                if(Ext.isDefined(field.getLookupData)) {
                                    e.record.set(field.name + "__label",
                                                 field.getLookupData());
                                }
                            });
                        }
                    },
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
        console.log(me.store);
        items = me.grid.store.getRange().map(function(x) {
            return {
                name: x.get("name"),
                rd: x.get("rd"),
                vrf_group: x.get("vrf_group"),
                afi_ipv4: x.get("afi_ipv4"),
                afi_ipv6: x.get("afi_ipv6"),
                description: x.get("description")
            }
        });
        data = {
            items: items
        };
        // @todo: Display mask
        // Save
        Ext.Ajax.request({
            url: "/ip/vrf/bulk/import/",
            method: "POST",
            scope: me,
            jsonData: data,
            success: function(response) {
                var r = Ext.decode(response.responseText);
                // @todo: Unmask
                this.close();
                Ext.Msg.show({
                    title: "Success!",
                    msg: Ext.String.format("{0} new VRFs has been imported",
                                           r.imported),
                    buttons: Ext.Msg.OK
                });
                this.app.onImportSuccess();
            },
            failure: function() {
                // @todo: Unmask
                NOC.error("Failed to save VRFs");
            }
        });
    },
    // Load data to Grid
    loadData: function(data) {
        var me = this;
        // Get existing VRFs
        Ext.Ajax.request({
            url: "/ip/vrf/",
            method: "GET",
            scope: me,
            success: function(response) {
                var me = this,
                    r = Ext.decode(response.responseText);
                // Fill existing VRFs's map
                me.existing_vrfs = {};
                Ext.each(r, function(x) {
                    me.existing_vrfs[x.rd] = true;
                });
                //
                // Left only new VRFs
                var d = data.filter(function(x) {
                    return !me.existing_vrfs[x.rd]
                });
                // Check new VRFs found
                if(d.length == 0) {
                    NOC.info("No new VRFs found");
                    me.close();
                } else {
                    // Load to store
                    me.grid.store.loadData(d);
                }
            },
            failure: function() {
                NOC.error("Failed to get existing VRF");
                me.close();
            }
        });
    },
    //
    // Load VRFs from get_mpls_vpn's result
    //
    loadVRFsFromRouter: function(data) {
        var me = this;
        // Filter only VRFs
        data = data.filter(function(x) {
            return x.type == "VRF";
        });
        // Convert data
        data = data.map(function(x) {
            return {
                name: x.name,
                rd: x.rd,
                afi_ipv4: true,
                afi_ipv6: false,
                description: x.description
            }
        });
        me.loadData(data);
    },
    //
    onRowEdit: function(editor) {
        var me = this,
            r = editor.record;
        r.commit();
    }
});
