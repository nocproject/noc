//---------------------------------------------------------------------
// Add Interfaces window
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vc.AddInterfacesForm");

Ext.define("NOC.vc.vc.AddInterfacesForm", {
    extend: "Ext.Window",
    requires: [
        "NOC.sa.managedobject.LookupField"
    ],
    autoShow: true,
    closable: true,
    maximizable: true,
    modal: true,
    vc: null,
    width: 600,
    height: 400,
    autoScroll: true,

    initComponent: function() {
        var me = this;
        me.store = Ext.create("NOC.vc.vc.AddInterfacesStore");
        Ext.apply(me, {
            title: Ext.String.format("Add interfaces to VC {0} ({1})",
                                     me.vc.name, me.vc.l1),
            items: [
                {
                    xtype: "gridpanel",
                    itemId: "grid",
                    store: me.store,
                    columns: [
                        {
                            header: "Managed Object",
                            dataIndex: "managed_object",
                            editor: "sa.managedobject.LookupField",
                            renderer: NOC.render.Lookup("managed_object")
                        },
                        {
                            header: "Interface",
                            dataIndex: "interface",
                            editor: "textfield"
                        },
                        {
                            header: "Description",
                            dataIndex: "description",
                            flex: 1,
                            editor: "textfield"
                        }, /*,
                        {
                            header: "Tag",
                            dataIndex: "tagged",
                            width: 35,
                            editor: "checkboxfield",
                            renderer: NOC.render.Bool
                        },*/
                        {
                            xtype: "actioncolumn",
                            width: 20,
                            items: [{
                                icon: "/static/img/fam/silk/delete.png",
                                tooltip: "Delete",
                                handler: function(grid, rowIndex, colIndex) {
                                    grid.getStore().removeAt(rowIndex);
                                }
                            }]
                        }
                    ],
                    selType: "rowmodel",
                    plugins: [
                        Ext.create("Ext.grid.plugin.RowEditing", {
                            clicksToEdit: 1
                        })
                    ],
                    listeners: {
                        validateedit: function(editor, e) {
                            // @todo: Bring to plugin
                            var form = editor.editor.getForm();
                            // Process comboboxes
                            form.getFields().each(function(field) {
                                e.record.set(field.name, field.getValue());
                                if(Ext.isDefined(field.getLookupData))
                                    e.record.set(field.name + "__label",
                                                 field.getLookupData());
                                });
                        }
                    },
                    tbar: [
                        {
                            text: "Apply",
                            iconCls: "icon_tick",
                            scope: me,
                            handler: function() {
                                me.apply();
                            }
                        }
                    ]
                }
            ]
        });
        me.callParent();
    },
    // Run tasks
    apply: function() {
        var me = this,
            mo = {};
        // Prepare data
        me.store.each(function(r) {
            var managed_object = r.get("managed_object"),
                interface = r.get("interface"),
                description = r.get("description");
            if(managed_object && interface) {
                var s = {
                    interface: interface,
                    untagged: me.vc.l1
                };
                if(description)
                    s.description = description;
                if(mo[managed_object])
                    mo[managed_object] = mo[managed_object].concat([s]);
                else
                    mo[managed_object] = [s];
            }
        }, me);
        // Run tasks
        me.mo = mo;
        me.runTasks();
    },
    runTasks: function() {
        var me = this;
        if(me.mo) {
            for(var o in me.mo) {
                NOC.mrt({
                    url: "/vc/vc/mrt/set_switchport/",
                    selector: o,
                    mapParams: {
                        configs: me.mo[o]
                    },
                    scope: me,
                    success: function(result) {
                        if(result.status.result.status) {
                            // Delete all successful interfaces from store
                        } else {

                        }

                        console.log("RESULT", result);
                        delete me.mo[o];
                        this.runTasks();
                    },
                    failure: function() {
                        NOC.error("Failed to apply VC settings");
                    }
                });
                break;
            }
        } else {
            Ext.info("All interface settings are applied successfully");
            me.close();
        }
    }
});
