//---------------------------------------------------------------------
// fm.event application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.event.Application");

Ext.define("NOC.fm.event.Application", {
    extend: "NOC.core.Application",
    requires: [
        "NOC.fm.event.templates.Overview",
        "NOC.fm.event.templates.Help",
        "NOC.fm.event.templates.Data"
    ],
    layout: "card",
    STATUS_MAP: {
        N: "New", A: "Active",
        F: "Failed", S: "Archived"
    },
    pollingInterval: 30000,
    //
    initComponent: function() {
        var me = this;
        me.currentQuery = {status: "A"};
        me.pollingTaskHandler = Ext.bind(me.pollingTask, me);
        me.store = Ext.create("NOC.core.ModelStore", {
            model: "NOC.fm.event.Model",
            autoLoad: false,
            pageSize: 1,
            customFields: [],
            filterParams: {
                status: "A"
            }
        });

        me.typeCombo = Ext.create("Ext.form.ComboBox", {
            fieldLabel: "State",
            labelWidth: 30,
            queryMode: "local",
            displayField: "name",
            valueField: "id",
            store: Ext.create("Ext.data.Store", {
                fields: ["id", "name"],
                data: [
                    {id: "N", name: "New"},
                    {id: "A", name: "Active"},
                    {id: "S", name: "Archived"},
                    {id: "F", name: "Failed"}
                ]
            }),
            value: "A",
            width: 110,
            listeners: {
                select: {
                    scope: me,
                    fn: me.onSelectType
                }
            }
        });

        me.objectCombo = Ext.create("NOC.sa.managedobject.LookupField", {
            fieldLabel: "Object",
            labelWidth: 40,
            width: 200,
            listeners: {
                scope: me,
                select: me.onSelectObject,
                clear: me.onClearObject
            }
        });

        /*
        me.eventClassCombo = Ext.create("NOC.fm.eventclass.LookupField", {
            fieldLabel: "Class",
            labelWidth: 40,
            width: 200
        });
        */

        me.gridPanel = Ext.create("Ext.grid.Panel", {
            store: me.store,
            features: [{
                ftype: "selectable",
                id: "selectable"
            }],
            border: false,
            stateful: true,
            stateId: "fm.event-grid",
            plugins: [Ext.create("Ext.ux.grid.AutoSize")],
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        me.typeCombo,
                        me.objectCombo,
                        // me.eventClassCombo
                    ]
                },
                {
                    xtype: "pagingtoolbar",
                    store: me.store,
                    dock: "bottom",
                    displayInfo: true
                }
            ],
            columns: [
                {
                    text: "ID",
                    dataIndex: "id",
                    width: 150
                },
                {
                    text: "Status",
                    dataIndex: "status",
                    width: 50,
                    renderer: NOC.render.Choices(me.STATUS_MAP)
                },
                {
                    text: "Time",
                    dataIndex: "timestamp",
                    width: 100,
                    renderer: NOC.render.DateTime
                },
                {
                    text: "Object",
                    dataIndex: "managed_object",
                    width: 200,
                    renderer: NOC.render.Lookup("managed_object")
                },
                {
                    text: "Class",
                    dataIndex: "event_class",
                    width: 300,
                    renderer: NOC.render.Lookup("event_class")
                },
                {
                    text: "Subject",
                    dataIndex: "subject",
                    flex: 1
                },
                {
                    text: "Alrm.",
                    dataIndex: "alarms",
                    width: 30,
                    align: "right"
                },
                {
                    text: "Rep.",
                    dataIndex: "repeats",
                    width: 30,
                    align: "right"
                },
                {
                    text: "Dur.",
                    dataIndex: "duration",
                    width: 30,
                    align: "right"
                }
            ],
            selModel: Ext.create("Ext.selection.CheckboxModel"),
            listeners: {
                itemdblclick: {
                    scope: me,
                    fn: me.onSelectEvent
                }
            },
            viewConfig: {
                getRowClass: Ext.bind(me.getRowClass, me)
                /* listeners: {
                    scope: me,
                    cellclick: me.onCellClick
                }*/
            }
        });
        //
        me.eventPanel = Ext.create("NOC.fm.event.EventPanel", {
            app: me
        });
        //
        Ext.apply(me, {
            items: [
                me.gridPanel,
                me.eventPanel
            ]
        });
        me.callParent();
        //
        me.reloadStore();
        //
        me.startPolling();
    },
    //
    reloadStore: function() {
        var me = this;
        if(me.currentQuery)
            me.store.setFilterParams(me.currentQuery);
        me.store.load();
    },
    //
    onSelectType: function(combo, records, opts) {
        var me = this;
        me.currentQuery.status = records[0].get("id");
        me.reloadStore();
    },
    //
    onSelectObject: function(combo, records, opts) {
        var me = this;
        me.currentQuery.managed_object = records[0].get("id");
        me.reloadStore();
    },
    //
    onClearObject: function() {
        var me = this;
        delete me.currentQuery.managed_object;
        me.reloadStore();
    },
    // Return Grid's row classes
    getRowClass: function(record, index, params, store) {
        var me = this,
            c = record.get("row_class");
        if(c) {
            return c;
        } else {
            return "";
        }
    },
    //
    showGrid: function() {
        var me = this;
        me.getLayout().setActiveItem(0);
        me.reloadStore();
        me.startPolling();
    },
    //
    onSelectEvent: function(grid, record, item, index) {
        var me = this;
        me.stopPolling();
        me.getLayout().setActiveItem(1);
        me.eventPanel.showEvent(record.get("id"));
    },
    //
    pollingTask: function() {
        var me = this;
        me.reloadStore();
    },
    //
    startPolling: function() {
        var me = this;
        me.pollingTaskId = Ext.TaskManager.start({
            run: me.pollingTaskHandler,
            interval: me.pollingInterval
        });
    },
    //
    stopPolling: function() {
        var me = this;
        Ext.TaskManager.stop(me.pollingTaskId);
    }
});
