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
    layout: "fit",

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
                    layout: "fit",
                    columns: [
                        {
                            xtype: "glyphactioncolumn",
                            itemId: "error",
                            width: 25,
                            hidden: true,
                            items: [
                                {
                                    glyph: NOC.glyph.exclamation_triangle,
                                    sortable: false,
                                    scope: me,
                                    handler: me.onShowError
                                }
                            ]
                        },
                        {
                            header: "Managed Object",
                            dataIndex: "managed_object",
                            editor: "sa.managedobject.LookupField",
                            renderer: NOC.render.Lookup("managed_object"),
                            width: 200
                        },
                        {
                            header: "Interface",
                            dataIndex: "interface",
                            editor: "textfield",
                            itemId: "interface",
                            width: 100
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
                                    handler: me.onDeleteRecord
                                }
                            ]
                        }
                    ],
                    selType: "rowmodel",
                    plugins: [
                        Ext.create("Ext.grid.plugin.RowEditing", {
                            clicksToEdit: 1,
                            listeners: {
                                edit: {
                                    scope: me,
                                    fn: me.onRowEdit
                                }
                            }
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
                            glyph: NOC.glyph.save,
                            scope: me,
                            handler: me.applyChanges
                        }
                    ]
                }
            ]
        });
        me.callParent();
        me.grid = me.getComponent("grid");
        me.errorColumn = me.grid.dockedItems.first().getComponent("error");
    },
    // Run tasks
    applyChanges: function() {
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
                    untagged: me.vc.l1,
                    status: true
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
        console.log(mo);
        me.runTasks();
    },
    runTasks: function() {
        var me = this,
            stopped = true;
        for(var o in me.mo) {
            NOC.mrt({
                url: "/vc/vc/mrt/set_switchport/",
                selector: o,
                mapParams: {
                    configs: me.mo[o]
                },
                scope: me,
                success: me.processTaskResult,
                failure: function() {
                    NOC.error("Failed to apply interface settings");
                }
            });
            stopped = false;
            break;
        }
        console.log(stopped);
        if(stopped) {
            console.log("Stopped", me.store);
            var success = true;
            me.store.each(function(r) {
                if(r.get("interface"))
                    success = false;
            });
            if(success) {
                NOC.info("All interface settings has been applied successfully");
                me.close();
            } else {
                NOC.error("Failed to apply some interfaces settings");
                me.showErrors();
            }
        }
    },
    // Process MRT result
    processTaskResult: function(result) {
        var me = this;
        Ext.each(result, function(r) {
            if(r.status) {
                // Filter out successfull objects
                me.store.filterBy(function(record) {
                    return record.get("managed_object") != r.object_id;
                });
                // dirty hack to apply filter permanently
                delete me.store.snapshot;
            } else {
                // Write Error Message
                var m = r.result.text;
                me.store.each(function(record) {
                    if((record.get("managed_object") == r.object_id) &&
                        record.get("interface")) {
                        record.set("error", m);
                        me.showErrors();
                    }
                });
            }
            delete me.mo[r.object_id];
        });
        me.runTasks();
    },
    onDeleteRecord: function(grid, rowIndex, colIndex) {
        var me = this;
        me.store.removeAt(rowIndex);
    },
    onShowError: function(grid, rowIndex, colIndex) {
        var me = this,
            error = me.store.getAt(rowIndex).get("error");
        Ext.create("NOC.core.LogWindow", {title: "Error!", msg: error});
    },
    showErrors: function() {
        this.errorColumn.show();
    },
    onRowEdit: function(editor) {
        var me = this,
            r = editor.record;
        r.commit();
        if(me.store.last() == r) {
            me.store.add({
                managed_object: r.get("managed_object"),
                managed_object__label: r.get("managed_object__label")
            });
            // editor.startEdit(me.store.last(), me.grid.columns[2]);
        }
    }
});
