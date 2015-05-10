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
    pollingInterval: 10000,
    //
    initComponent: function() {
        var me = this,
            bs = Math.max(50, Math.ceil(screen.height / 24) + 10);
        me.pollingTaskId = null;
        me.currentQuery = {status: "A"};
        me.store = Ext.create("NOC.core.ModelStore", {
            model: "NOC.fm.event.Model",
            autoLoad: false,
            customFields: [],
            filterParams: {
                status: "A"
            },
            pageSize: bs,
            leadingBufferZone: bs,
            numFromEdge: bs,
            trailingBufferZone: bs
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
                    fn: me.onChangeFilter
                }
            }
        });

        me.objectCombo = Ext.create("NOC.sa.managedobject.LookupField", {
            fieldLabel: "Object",
            labelWidth: 40,
            width: 200,
            listeners: {
                scope: me,
                select: me.onChangeFilter,
                clear: me.onChangeFilter
            }
        });

        me.selectorCombo = Ext.create("NOC.sa.managedobjectselector.LookupField", {
            fieldLabel: "Selector",
            labelWidth: 40,
            width: 200,
            listeners: {
                scope: me,
                select: me.onChangeFilter,
                clear: me.onChangeFilter
            }
        });

        me.admdomCombo = Ext.create("NOC.sa.administrativedomain.LookupField", {
            fieldLabel: "Adm. Domain",
            labelWidth: 40,
            width: 200,
            listeners: {
                scope: me,
                select: me.onChangeFilter,
                clear: me.onChangeFilter
            }
        });

        me.eventClassCombo = Ext.create("NOC.fm.eventclass.LookupField", {
            fieldLabel: "Class",
            labelWidth: 40,
            width: 300,
            listeners: {
                scope: me,
                select: me.onChangeFilter,
                clear: me.onChangeFilter
            }
        });

        me.fromDateField = Ext.create("Ext.form.field.Date", {
            fieldLabel: "From",
            labelWidth: 35,
            format: "d.m.Y",
            width: 130,
            listeners: {
                scope: me,
                select: me.onChangeFilter
            }
        });

        me.toDateField = Ext.create("Ext.form.field.Date", {
            fieldLabel: "To",
            labelWidth: 25,
            format: "d.m.Y",
            width: 120,
            listeners: {
                scope: me,
                select: me.onChangeFilter
            }
        });

        me.gridPanel = Ext.create("Ext.grid.Panel", {
            store: me.store,
            border: false,
            itemId: "grid-panel",
            stateful: true,
            stateId: "fm.event-grid",
            plugins: [
                {
                    ptype: "bufferedrenderer"
                    //trailingBufferZone: 50,
                    //leadingBufferZone: 50
                }
            ],
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    layout: {
                        overflowHandler: "Menu"
                    },
                    items: [
                        me.typeCombo,
                        me.admdomCombo,
                        me.selectorCombo,
                        me.objectCombo,
                        me.eventClassCombo,
                        me.fromDateField,
                        me.toDateField
                    ]
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
                    renderer: NOC.render.Choices(me.STATUS_MAP),
                    hidden: true
                },
                {
                    text: "Time",
                    dataIndex: "timestamp",
                    width: 100,
                    renderer: NOC.render.DateTime
                },
                {
                    text: "Administrative Domain",
                    dataIndex: "administrative_domain",
                    width: 200,
                    renderer: NOC.render.Lookup("administrative_domain")
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
                    width: 70,
                    align: "right",
                    renderer: NOC.render.Duration
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
                enableTextSelection: true,
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
        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: "/fm/event/{{id}}/json/",
            previewName: "Event: {{id}}"
        });
        me.ITEM_GRID = me.registerItem(me.gridPanel);
        me.ITEM_FORM = me.registerItem(me.eventPanel);
        me.ITEM_JSON = me.registerItem(me.jsonPanel);
        Ext.apply(me, {
            items: me.getRegisteredItems()
        });
        me.callParent();
        //
        me.startPolling();
        if(me.getCmd() === "history") {
            me.showEvent(me.noc.cmd.args[0]);
        }

    },
    //
    reloadStore: function() {
        var me = this;
        if(me.currentQuery) {
            me.store.setFilterParams(me.currentQuery);
        }
        me.store.load();
    },
    //
    onChangeFilter: function() {
        var me = this,
            q = {},
            setIf = function(k, v) {
                if(v) {
                    q[k] = v;
                }
            };

        // Status
        q.status = me.typeCombo.getValue();
        // Selector
        setIf("managedobjectselector", me.selectorCombo.getValue());
        // Adm Domain
        setIf("administrative_domain", me.admdomCombo.getValue());
        // Object
        setIf("managed_object", me.objectCombo.getValue());
        // Class
        setIf("event_class", me.eventClassCombo.getValue());
        // From Date
        setIf("timestamp__gte", me.fromDateField.getValue());
        // To Date
        setIf("timestamp__lte", me.toDateField.getValue());
        //
        me.currentQuery = q;
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
    // Returns true if polling is locked
    isPollLocked: function() {
        var me = this,
            ls;
        ls = me.gridPanel.getView().getScrollable().getPosition().y !== 0;
        return ls;
    },
    //
    pollingTask: function() {
        var me = this;
        // Poll only application tab is visible
        if(!me.isActiveApp()) {
            return;
        }
        // Poll only when in grid preview
        if(me.getLayout().getActiveItem().itemId !== "grid-panel") {
            return;
        }
        // Poll only if polling is not locked
        if(!me.isPollLocked()) {
            me.store.load();
        }
    },
    //
    startPolling: function() {
        var me = this;
        if(me.pollingTaskId) {
            me.pollingTask();
        } else {
            me.pollingTaskId = Ext.TaskManager.start({
                run: me.pollingTask,
                interval: me.pollingInterval,
                scope: me
            });
        }
    },
    //
    stopPolling: function() {
        var me = this;
        if(me.pollingTaskId) {
            Ext.TaskManager.stop(me.pollingTaskId);
            me.pollingTaskId = null;
        }
    },
    //
    showForm: function() {
        var me = this;
        me.showItem(me.ITEM_FORM);
    },
    //
    showEvent: function(id) {
        var me = this,
            panel = me.showItem(me.ITEM_FORM);
        panel.showEvent(id);
    },
    //
    onCloseApp: function() {
        var me = this;
        me.stopPolling();
    }
});
