//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.Application");

Ext.define("NOC.fm.alarm.Application", {
    extend: "NOC.core.Application",
    requires: [
        "NOC.fm.alarm.templates.Overview",
        "NOC.fm.alarm.templates.Help",
        "NOC.fm.alarm.templates.Data",
        "NOC.fm.alarm.templates.SummaryPanel"
    ],
    layout: "card",
    STATUS_MAP: {
        A: "Active",
        C: "Archived"
    },
    pollingInterval: 30000,
    //
    initComponent: function() {
        var me = this,
            bs = Math.max(50, Math.ceil(screen.height / 24) + 10);
        me.pollingTaskId = null;
        me.lastCheckTS = null;
        me.sounds = {};  // url -> audio object
        me.currentQuery = {status: "A"};
        me.store = Ext.create("NOC.core.ModelStore", {
            model: "NOC.fm.alarm.Model",
            autoLoad: false,
            customFields: [],
            filterParams: {
                status: "A",
                collapse: 1
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
                    {id: "A", name: "Active"},
                    {id: "C", name: "Archived"},
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

        me.admdomCombo = Ext.create("NOC.sa.administrativedomain.LookupField", {
            fieldLabel: _("Adm. Domain"),
            labelWidth: 40, 
            width: 200,
            listeners: {
                scope: me, 
                select: me.onChangeFilter,
                clear: me.onChangeFilter
            }   
        }); 

        me.objectCombo = Ext.create("NOC.sa.managedobject.LookupField", {
            fieldLabel: _("Object"),
            labelWidth: 40,
            width: 200,
            listeners: {
                scope: me,
                select: me.onChangeFilter,
                clear: me.onChangeFilter
            }
        });

        me.selectorCombo = Ext.create("NOC.sa.managedobjectselector.LookupField", {
            fieldLabel: _("Selector"),
            labelWidth: 40, 
            width: 200,
            listeners: {
                scope: me, 
                select: me.onChangeFilter,
                clear: me.onChangeFilter
            }   
        }); 

        me.alarmClassCombo = Ext.create("NOC.fm.alarmclass.LookupField", {
            fieldLabel: _("Class"),
            labelWidth: 40,
            width: 300,
            listeners: {
                scope: me,
                select: me.onChangeFilter,
                clear: me.onChangeFilter
            }
        });

        me.fromDateField = Ext.create("Ext.form.field.Date", {
            fieldLabel: _("From"),
            labelWidth: 35,
            format: "d.m.Y",
            width: 130,
            listeners: {
                scope: me,
                select: me.onChangeFilter
            }
        });

        me.toDateField = Ext.create("Ext.form.field.Date", {
            fieldLabel: _("To"),
            labelWidth: 25,
            format: "d.m.Y",
            width: 120,
            listeners: {
                scope: me,
                select: me.onChangeFilter
            }
        });

        me.expandButton = Ext.create("Ext.button.Button", {
            text: _("Expand"),
            tooltip: _("Show/collapse children alarms"),
            enableToggle: true,
            glyph: NOC.glyph.expand,
            scope: me,
            handler: me.onChangeFilter
        });

        me.gridPanel = Ext.create("Ext.grid.Panel", {
            store: me.store,
            border: false,
            itemId: "grid-panel",
            stateful: true,
            stateId: "fm.alarm-grid",
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
                        me.selectorCombo,
                        me.admdomCombo,
                        me.objectCombo,
                        me.alarmClassCombo,
                        me.fromDateField,
                        me.toDateField,
                        me.expandButton
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
                    text: _("Status"),
                    dataIndex: "status",
                    width: 50,
                    renderer: NOC.render.Choices(me.STATUS_MAP),
                    hidden: true
                },
                {
                    text: _("Time"),
                    dataIndex: "timestamp",
                    width: 100,
                    renderer: NOC.render.DateTime
                },
                {
                    text: _("Segment"),
                    dataIndex: "segment",
                    width: 200,
                    renderer: NOC.render.Lookup("segment")
                },
                {
                    text: _("Object"),
                    dataIndex: "managed_object",
                    width: 200,
                    renderer: NOC.render.Lookup("managed_object")
                },
                {
                    text: _("Severity"),
                    dataIndex: "severity",
                    width: 70,
                    renderer: NOC.render.Lookup("severity")
                },
                {
                    text: _("Class"),
                    dataIndex: "alarm_class",
                    width: 300,
                    renderer: NOC.render.Lookup("alarm_class")
                },
                {
                    text: _("Subject"),
                    dataIndex: "subject",
                    flex: 1
                },
                {
                    text: _("Duration"),
                    dataIndex: "duration",
                    width: 70,
                    align: "right",
                    renderer: NOC.render.Duration
                },
                {
                    text: _("Events"),
                    dataIndex: "events",
                    width: 30,
                    align: "right"
                }
            ],
            selModel: Ext.create("Ext.selection.CheckboxModel"),
            listeners: {
                itemdblclick: {
                    scope: me,
                    fn: me.onSelectAlarm
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
        me.alarmPanel = Ext.create("NOC.fm.alarm.AlarmPanel", {
            app: me
        });
        me.ITEM_GRID = me.registerItem(me.gridPanel);
        me.ITEM_FORM = me.registerItem(me.alarmPanel);
        Ext.apply(me, {
            items: me.getRegisteredItems()
        });
        me.callParent();
        //
        me.startPolling();
        //
        switch(me.getCmd) {
            case "history":
                me.showAlarm(me.noc.cmd.args[0]);
                break;
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
        setIf("alarm_class", me.alarmClassCombo.getValue());
        // From Date
        setIf("timestamp__gte", me.fromDateField.getValue());
        // To Date
        setIf("timestamp__lte", me.toDateField.getValue());
        // Expand
        if(!me.expandButton.pressed) {
            q.collapse = 1;
        }
        me.currentQuery = q;
        me.reloadStore();
    },
    // Return Grid's row classes
    getRowClass: function(record, index, params, store) {
        var c = record.get("row_class");
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
        //me.reloadStore();
        me.startPolling();
        me.setHistoryHash();
    },
    //
    onSelectAlarm: function(grid, record, item, index) {
        var me = this;
        me.stopPolling();
        me.getLayout().setActiveItem(1);
        me.alarmPanel.showAlarm(record.get("id"));
    },
    // Returns true if polling is locked
    isPollLocked: function() {
        var me = this,
            ls;
        ls = me.gridPanel.getView().getScrollable().getPosition().y !== 0;
        return ls;
    },
    //
    pollingTask: function () {
        var me = this;
        // Check for new alarms and play sound
        me.checkNewAlarms();
        // Poll only application tab is visible
        if (!me.isActiveApp()) {
            return;
        }
        // Poll only when in grid preview
        if (me.getLayout().getActiveItem().itemId !== "grid-panel") {
            return;
        }
        // Poll only if polling is not locked
        if (!me.isPollLocked()) {
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
    showAlarm: function(id) {
        var me = this,
            panel = me.showItem(me.ITEM_FORM);
        panel.showAlarm(id);
    },
    //
    onCloseApp: function() {
        var me = this;
        me.stopPolling();
    },
    //
    checkNewAlarms: function() {
        var me = this,
            ts, delta;
        ts = new Date().getTime();
        if(me.lastCheckTS) {
            delta = Math.ceil((ts - me.lastCheckTS) / 1000.0);
            Ext.Ajax.request({
                url: "/fm/alarm/notification/?delta=" + delta,
                scope: me,
                success: function (response) {
                    var data = Ext.decode(response.responseText);
                    if (data.sound) {
                        if (!me.sounds[data.sound]) {
                            me.sounds[data.sound] = new Audio(data.sound);
                        }
                        me.sounds[data.sound].play();
                    }
                }
            });
        }
        me.lastCheckTS = ts;
    }
});
