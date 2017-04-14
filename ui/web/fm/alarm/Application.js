//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.Application");

Ext.define("NOC.fm.alarm.Application", {
    extend: "NOC.core.Application",
    layout: "card",
    mixins: [
        "NOC.core.Export"
    ],
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
        me.currentQuery = {
            status: "A",
            maintainance: "hide"
        };
        me.store = Ext.create("NOC.core.ModelStore", {
            model: "NOC.fm.alarm.Model",
            autoLoad: false,
            customFields: [],
            filterParams: {
                status: "A",
                collapse: 1
            },
            remoteSort: true,
            sorters: [
                {
                    property: 'timestamp',
                    direction: 'DESC'
                }
            ],
            pageSize: bs,
            leadingBufferZone: bs,
            numFromEdge: bs,
            trailingBufferZone: bs,
            listeners: {
                scope: me,
                load: me.onLoad
            }
        });

        me.autoreloadButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.refresh,
            enableToggle: true,
            pressed: false,
            tooltip: __("Toggle autoreload"),
            listeners: {
                scope: me,
                toggle: me.onAutoReloadToggle
            }
        });

        me.soundButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.volume_off,
            enableToggle: true,
            pressed: false,
            tooltip: __("Toggle sound"),
            listeners: {
                scope: me,
                toggle: me.onSoundToggle
            }
        });

        me.typeButton = Ext.create("Ext.button.Segmented", {
            items: [
                {
                    text: __("Active"),
                    pressed: true,
                    tooltip: __("Show active alarms"),
                    width: 99
                },
                {
                    text: __("Archive"),
                    tooltip: __("Show archived alarms")
                }
            ],
            listeners: {
                scope: me,
                toggle: me.onChangeFilter
            }
        });

        me.admdomCombo = Ext.create("NOC.sa.administrativedomain.TreeCombo", {
            fieldLabel: __("Adm. Domain"),
            width: 198,
            listeners: {
                scope: me,
                select: me.onChangeFilter,
                change: me.onChange,
                clear: me.onChangeFilter
            },
            uiStyle: null
        }); 

        me.objectCombo = Ext.create("NOC.sa.managedobject.LookupField", {
            fieldLabel: __("Object"),
            width: 198,
            listeners: {
                scope: me,
                select: me.onChangeFilter,
                change: me.onChange,
                clear: me.onChangeFilter
            }
        });

        me.selectorCombo = Ext.create("NOC.sa.managedobjectselector.LookupField", {
            fieldLabel: __("Selector"),
            width: 198,
            listeners: {
                scope: me,
                select: me.onChangeFilter,
                change: me.onChange,
                clear: me.onChangeFilter
            }   
        }); 

        me.segmentCombo = Ext.create("NOC.inv.networksegment.TreeCombo", {
            fieldLabel: __("Segment"),
            width: 198,
            listeners: {
                scope: me,
                select: me.onChangeFilter,
                change: me.onChange,
                clear: me.onChangeFilter
            }
        });

        me.alarmClassCombo = Ext.create("NOC.fm.alarmclass.LookupField", {
            fieldLabel: __("Class"),
            width: 198,
            listeners: {
                scope: me,
                select: me.onChangeFilter,
                change: me.onChange,
                clear: me.onChangeFilter
            }
        });

        me.fromDateField = Ext.create("Ext.form.field.Date", {
            tooltip: __("From"),
            format: "d.m.Y",
            width: 95,
            listeners: {
                scope: me,
                change: me.onChangeFilter
            }
        });

        me.toDateField = Ext.create("Ext.form.field.Date", {
            tooltip: __("To"),
            format: "d.m.Y",
            width: 95,
            listeners: {
                scope: me,
                change: me.onChangeFilter
            }
        });

        me.expandButton = Ext.create("Ext.button.Segmented", {
            items: [
                {
                    text: __("Root only"),
                    pressed: true,
                    tooltip: __("Show only root causes"),
                    width: 99
                },
                {
                    text: __("All"),
                    tooltip: __("Show all alarms")
                }
            ],
            listeners: {
                scope: me,
                toggle: me.onChangeFilter
            }
        });

        me.ttConfirmButton = Ext.create("Ext.button.Segmented", {
            items: [
                {
                    text: __("Wait TT"),
                    tooltip: __("Show only waiting confirmantion"),
                    width: 99
                },
                {
                    text: __("All"),
                    pressed: true,
                    tooltip: __("Show all alarms")
                }
            ],
            listeners: {
                scope: me,
                toggle: me.onChangeFilter
            }
        });

        me.maintainanceButton = Ext.create("Ext.button.Segmented", {
            items: [
                {
                    text: __("Hide maintainance"),
                    tooltip: __("Hide alarms covered by maintainance"),
                    pressed: true,
                    filterExpression: "hide"
                },
                {
                    text: __("Show"),
                    tooltip: __("Show all alarms"),
                    filterExpression: "show"
                },
                {
                    text: __("Only"),
                    tooltip: __("Show only alarms covered by maintainance"),
                    filterExpression: "only"
                }
            ],
            listeners: {
                scope: me,
                toggle: me.onChangeFilter
            }
        });

        me.gridMenu = Ext.create("Ext.menu.Menu", {
            items: [
                {
                    text: __("Refresh"),
                    glyph: NOC.glyph.refresh,
                    scope: me,
                    handler: me.onContextMenuRefresh
                },
                {
                    text: __("Save screen"),
                    glyph: NOC.glyph.arrow_down,
                    scope: me,
                    handler: function() {
                        this.save(me.gridPanel, "alarms.csv")
                    }
                },
                {
                    text: __("Filter"),
                    glyph: NOC.glyph.filter,
                    menu: [
                        {
                            text: __("Object"),
                            scope: me,
                            itemId: "filterByObject",
                            handler: me.onContextMenuFilter
                        },
                        {
                            text: __("Segment"),
                            scope: me,
                            itemId: "filterBySegment",
                            handler: me.onContextMenuFilter
                        },
                        {
                            text: __("Class"),
                            scope: me,
                            itemId: "filterByClass",
                            handler: me.onContextMenuFilter
                        }
                    ]
                }
            ]
        });
        me.currentAlarm = null;

        me.gridPanel = Ext.create("Ext.grid.Panel", {
            store: me.store,
            border: false,
            itemId: "grid-panel",
            stateful: true,
            stateId: "fm.alarm-grid",
            // plugins: [
            //     {
            //         ptype: "bufferedrenderer"
            //         //trailingBufferZone: 50,
            //         //leadingBufferZone: 50
            //     }
            // ],
            dockedItems: [
                {
                    xtype: "form",
                    itemId: "filtertoolbar",
                    width: 208,
                    title: __("Filter"),
                    dock: "right",
                    padding: 4,
                    autoScroll: true,
                    defaults: {
                        labelAlign: "top",
                        padding: 4
                    },
                    items: [
                        me.autoreloadButton,
                        me.soundButton,
                        me.typeButton,
                        me.expandButton,
                        me.ttConfirmButton,
                        me.maintainanceButton,
                        me.objectCombo,
                        me.segmentCombo,
                        me.admdomCombo,
                        me.selectorCombo,
                        me.alarmClassCombo,
                        {
                            xtype: "fieldset",
                            layout: "hbox",
                            title: __("By Date"),
                            items: [
                                me.fromDateField,
                                me.toDateField
                            ]
                        }
                    ]
                }
            ],
            columns: [
                {
                    text: __("ID"),
                    dataIndex: "id",
                    width: 150,
                    hidden: true
                },
                {
                    xtype: "glyphactioncolumn",
                    width: 20 * 2,
                    sortable: false,
                    items: [
                        {
                            glyph: NOC.glyph.globe,
                            tooltip: __("Show map"),
                            scope: me,
                            handler: me.onShowMap
                        },
                        {
                            glyph: NOC.glyph.eye,
                            tooltip: __("Show object"),
                            scope: me,
                            handler: me.onShowObject
                        }
                    ]
                },
                {
                    text: __("Status"),
                    dataIndex: "status",
                    width: 50,
                    renderer: function(v, _, record){
                        var value = NOC.render.Choices(me.STATUS_MAP)(v);
                        if(record.get('isInMaintenance')) value = '<span title="' + __('Under maintaintance') + '">' +
                            '<i class="fa fa-wrench" aria-hidden="true"></i>&nbsp;' + value + '</span>';
                        return value;
                    },
                    hidden: true
                },
                {
                    text: __("Time/Duration"),
                    dataIndex: "timestamp",
                    width: 120,
                    renderer: function(v, _, record) {
                        return NOC.render.DateTime(record.get("timestamp")) +
                            "<br/>" +
                            NOC.render.Duration(record.get("duration"));
                    }
                },
                {
                    text: __("Object/Segment"),
                    dataIndex: "managed_object",
                    width: 250,
                    renderer: function(v, _, record) {
                        return record.get("managed_object__label") + "<br/>" + record.get("segment__label");
                    }
                },
                {
                    text: __("Address/Platform"),
                    dataIndex: "address",
                    width: 120,
                    renderer: function(_, _, record) {
                        return record.get("address") +
                            "<br/>" +
                            (record.get("platform") || "");
                    }
                },
                {
                    text: __("Severity"),
                    dataIndex: "severity",
                    width: 70,
                    renderer: function(v, _, record) {
                        return record.get("severity__label") +
                                "<br/>" +
                                record.get("severity");
                    }
                },
                {
                    text: __("Subject/Class"),
                    dataIndex: "subject",
                    flex: 1,
                    sortable: false,
                    renderer: function(v, _, record) {
                        return record.get("subject") +
                                "<br/>" +
                                record.get("alarm_class__label");
                    }
                },
                {
                    text: __("Summary/TT"),
                    dataIndex: "summary",
                    width: 150,
                    sortable: false,
                    renderer: function(v, _, record) {
                        var tt = record.get("escalation_tt");
                        return record.get("summary") +
                                "<br/>" +
                            (tt ? "<a href='/api/card/view/tt/" + tt + "/' target='_blank'>" + tt + "</a>" : "");

                    }
                },
                {
                    text: __("Objects"),
                    dataIndex: "total_objects",
                    width: 30,
                    align: "right",
                    sortable: false
                },
                {
                    text: __("Events"),
                    dataIndex: "events",
                    width: 30,
                    align: "right",
                    sortable: false
                }
            ],
            //selModel: Ext.create("Ext.selection.CheckboxModel"),
            listeners: {
                scope: me,
                itemdblclick: me.onSelectAlarm
            },
            viewConfig: {
                enableTextSelection: true,
                getRowClass: Ext.bind(me.getRowClass, me),
                loadMask: false,
                listeners: {
                    scope: me,
                    itemcontextmenu: me.onGridContextMenu,
                    beforerefresh: function(cmp){
                        me.gridPanel.plugins[0].bodyTop = 0;
                    }
                }
            }
        });
        //
        me.filterPanel = me.gridPanel.getComponent("filtertoolbar");
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
        q.status = me.typeButton.items.first().pressed ? "A" : "C";
        // Expand
        if(me.expandButton.items.first().pressed) {
            q.collapse = 1;
        }
        if(me.ttConfirmButton.items.first().pressed) {
            q.wait_tt = 1;
        }
        me.maintainanceButton.items.each(function(b) {
            if(b.pressed) {
                q["maintainance"] = b.filterExpression;
                return false;
            }
            return true;
        });
        // Selector
        setIf("managedobjectselector", me.selectorCombo.getValue());
        // Adm Domain
        setIf("administrative_domain", me.admdomCombo.getValue());
        // Segment
        setIf("segment", me.segmentCombo.getValue());
        // Object
        setIf("managed_object", me.objectCombo.getValue());
        // Class
        setIf("alarm_class", me.alarmClassCombo.getValue());
        // From Date
        setIf("timestamp__gte", me.fromDateField.getValue());
        // To Date
        setIf("timestamp__lte", me.toDateField.getValue());
        me.currentQuery = q;
        me.reloadStore();
    },
    //
    onChange: function(element, newValue) {
        if(newValue === null) {
            element.clearValue();
            this.onChangeFilter();
        }
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
        ls = me.autoreloadButton.pressed && (me.gridPanel.getView().getScrollable().getPosition().y === 0) && !me.gridMenu.isVisible();
        return !ls;
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
        if(me.lastCheckTS && me.soundButton.pressed) {
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
                        me.sounds[data.sound].volume = data.volume || 1.0;
                        me.sounds[data.sound].play();
                    }
                }
            });
        }
        me.lastCheckTS = ts;
    },
    //
    onAutoReloadToggle: function() {
        var me = this;
        if(me.autoreloadButton.pressed) {
            me.store.load();
        }
    },
    //
    onSoundToggle: function() {
        var me = this;
        if(me.soundButton.pressed) {
            me.soundButton.setGlyph(NOC.glyph.volume_up);
        } else {
            me.soundButton.setGlyph(NOC.glyph.volume_off);
        }
    },
    //
    onShowMap: function(grid, rowIndex) {
        var me = this,
            record = grid.store.getAt(rowIndex);
        NOC.launch("inv.map", "history", {
            args: [record.get("segment")]
        });
    },
    //
    onShowObject: function(grid, rowIndex) {
        var me = this,
            record = grid.store.getAt(rowIndex);
        NOC.launch("sa.managedobject", "history", {
            args: [record.get("managed_object")]
        });
    },
    //
    onLoad: function() {
        var me = this;
        me.filterPanel.setTitle(__("Total: ") + me.store.getTotalCount());
    },
    //
    onGridContextMenu: function(view, record, node, index, event) {
        var me = this;
        event.stopEvent();
        me.currentAlarm = record;
        me.gridMenu.showAt(event.getXY());
        return false;
    },
    //
    onContextMenuRefresh: function() {
        var me = this;
        me.onChangeFilter();
    },
    //
    onContextMenuFilter: function(item, event) {
        var me = this;
        switch(item.itemId) {
            case "filterByObject":
                me.objectCombo.setValue(
                    me.currentAlarm.get("managed_object"),
                    true
                );
                break;
            case "filterBySegment":
                me.segmentCombo.setValue(
                    me.currentAlarm.get("segment"),
                    true
                );
                break;
            case "filterByClass":
                me.alarmClassCombo.setValue(
                    me.currentAlarm.get("alarm_class"),
                    true
                );
                break;
        }
    }
});
