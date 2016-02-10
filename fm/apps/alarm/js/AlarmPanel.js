//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.AlarmPanel");

Ext.define("NOC.fm.alarm.AlarmPanel", {
    extend: "Ext.panel.Panel",
    requires: [
        "NOC.fm.alarm.AlarmsModel"
    ],
    app: null,
    autoScroll: true,
    layout: {
        type: "vbox",
        pack: "start",
        align: "stretch"
    },

    initComponent: function() {
        var me = this;

        me.alarmIdField = Ext.create("Ext.form.DisplayField", {
            fieldLabel: "ID",
            labelWidth: 20,
            width: 190,
            labelClsExtra: "noc-label-required"
        });

        me.topPanel = Ext.create("Ext.panel.Panel", {
            height: 100,
            bodyPadding: 4,
            layout: "fit",
            items: [{
                xtype: "container",
                autoScroll: true,
                padding: 4
            }]
        });

        me.overviewPanel = Ext.create("Ext.panel.Panel", {
            title: "Overview",
            autoScroll: true
        });

        me.helpPanel = Ext.create("Ext.panel.Panel", {
            title: "Help",
            autoScroll: true
        });

        me.dataPanel = Ext.create("Ext.panel.Panel", {
            title: "Data",
            autoScroll: true
        });

        me.logStore = Ext.create("Ext.data.Store", {
            fields: [
                {
                    name: "timestamp",
                    type: "date"
                },
                "from_status", "to_status", "message"],
            data: []
        });

        me.messageField = Ext.create("Ext.form.TextField", {
            fieldLabel: "New message",
            labelWidth: 75,
            anchor: "100%",
            listeners: {
                specialkey: {
                    scope: me,
                    fn: me.onMessageKey
                }
            }
        });

        me.logPanel = Ext.create("Ext.grid.Panel", {
            title: "Log",
            store: me.logStore,
            autoScroll: true,
            columns: [
                {
                    dataIndex: "timestamp",
                    text: "Time",
                    renderer: NOC.render.DateTime,
                    width: 120
                },
                {
                    dataIndex: "from_status",
                    text: "From",
                    renderer: NOC.render.Choices(me.app.STATUS_MAP),
                    width: 50
                },
                {
                    dataIndex: "to_status",
                    text: "To",
                    renderer: NOC.render.Choices(me.app.STATUS_MAP),
                    width: 50
                },
                {
                    dataIndex: "message",
                    text: "Message",
                    flex: 1
                }
            ],
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "bottom",
                    items: [me.messageField]
                }
            ]
        });
        //
        me.eventsStore = Ext.create("NOC.fm.alarm.EventsStore");
        me.eventsPanel = Ext.create("Ext.grid.Panel", {
            title: "Events",
            store: me.eventsStore,
            autoScroll: true,
            columns: [
                {
                    dataIndex: "id",
                    text: "ID",
                    width: 150
                },
                {
                    dataIndex: "timestamp",
                    text: "Time",
                    renderer: NOC.render.DateTime,
                    width: 120
                },
                {
                    dataIndex: "event_class",
                    text: "Class",
                    renderer: NOC.render.Lookup("event_class"),
                    width: 200
                },
                {
                    dataIndex: "subject",
                    text: "Subject",
                    flex: 1
                }
            ]
        });
        // Alarms
        me.defaultRoot = {
            text: ".",
            children: []
        };

        me.alarmsStore = Ext.create("Ext.data.TreeStore", {
            model: "NOC.fm.alarm.AlarmsModel",
            root: me.defaultRoot
        });
        me.alarmsPanel = Ext.create("Ext.tree.Panel", {
            title: "Alarms",
            store: me.alarmsStore,
            rootVisible: false,
            useArrows: true,
            columns: [
                {
                    xtype: "treecolumn",
                    dataIndex: "id",
                    text: "ID",
                    width: 200
                },
                {
                    dataIndex: "timestamp",
                    text: "Time",
                    width: 120,
                    renderer: NOC.render.DateTime
                },
                {
                    dataIndex: "managed_object",
                    text: "Object",
                    width: 200,
                    renderer: NOC.render.Lookup("managed_object")
                },
                {
                    dataIndex: "alarm_class",
                    text: "Class",
                    renderer: NOC.render.Lookup("alarm_class")
                },
                {
                    dataIndex: "subject",
                    text: "Subject",
                    flex: 1
                }
            ],
            viewConfig: {
                getRowClass: function(record, index, params, store) {
                    var c = record.get("row_class");
                    return c ? c: "";
                }
            }
        });
        //
        me.tabPanel = Ext.create("Ext.tab.Panel", {
            flex: 1,
            items: [
                me.overviewPanel,
                me.helpPanel,
                me.dataPanel,
                me.logPanel,
                me.eventsPanel,
                me.alarmsPanel
            ]
        });

        me.clearButton = Ext.create("Ext.Button", {
            text: "Clear",
            glyph: NOC.glyph.eraser,
            scope: me,
            handler: me.onClear
        });

        me.watchButton = Ext.create("Ext.Button", {
            text: "Watch",
            enableToggle: true,
            glyph: NOC.glyph.star,
            scope: me,
            handler: me.onWatch
        });

        me.setRootButton = Ext.create("Ext.Button", {
            text: "Set Root Cause",
            glyph: NOC.glyph.paperclip,
            scope: me,
            handler: me.onSetRoot
        });

        me.showMapButton = Ext.create("Ext.button.Button", {
            text: "Show Map",
            glyph: NOC.glyph.globe,
            scope: me,
            handler: me.onShowMap
        });

        me.showObjectButton = Ext.create("Ext.button.Button", {
            text: "Show Object",
            glyph: NOC.glyph.eye,
            scope: me,
            handler: me.onShowObject
        });

        Ext.apply(me, {
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        {
                            text: "Close",
                            glyph: NOC.glyph.arrow_left,
                            scope: me,
                            handler: me.onClose
                        },
                        {
                            text: "Refresh",
                            glyph: NOC.glyph.refresh,
                            scope: me,
                            handler: me.onRefresh
                        },
                        "-",
                        me.clearButton,
                        me.watchButton,
                        me.setRootButton,
                        "-",
                        me.showMapButton,
                        me.showObjectButton,
                        "->",
                        me.alarmIdField
                    ]
                }
            ],
            items: [
                me.topPanel,
                me.tabPanel
            ]
        });

        me.plugins = [];
        me.callParent();
    },
    //
    showAlarm: function(alarmId) {
        var me = this;
        Ext.Ajax.request({
            url: "/fm/alarm/" + alarmId + "/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                me.updateData(data);
            },
            failure: function() {
                NOC.error("Failed to get alarm");
            }
        });
        me.app.setHistoryHash(alarmId);
    },
    //
    updatePanel: function(panel, template, enabled, data) {
        panel.setDisabled(!enabled);
        panel.setVisible(enabled);
        if(enabled) {
            panel.update("<div class='noc-tp'>" + template(data) + "</div>");
        }
    },
    //
    updateData: function(data) {
        var me = this,
            oldId = me.data ? me.data.id : undefined,
            o = [];
        me.data = data;
        //
        me.alarmIdField.setValue(me.data.id);
        me.topPanel.items.first().update(
            me.app.templates.SummaryPanel(me.data)
        );
        //
        me.updatePanel(me.overviewPanel, me.app.templates.Overview,
            data.subject, data);
        me.updatePanel(me.helpPanel, me.app.templates.Help,
            data.symptoms, data);
        me.updatePanel(me.dataPanel, me.app.templates.Data,
            (data.vars && data.vars.length)
                || (data.raw_vars && data.raw_vars.length)
                || (data.resolved_vars && data.resolved_vars.length),
            data);
        me.logStore.loadData(data.log || []);
        //
        me.eventsStore.loadData(data.events || []);
        me.eventsPanel.setDisabled(!data.events);
        //
        me.alarmsStore.setRootNode(data.alarms || me.defaultRoot);
        me.alarmsPanel.setDisabled(!data.alarms);
        // Subscribe/Clear button
        me.clearButton.setDisabled(me.data.status !== "A");
        me.watchButton.setDisabled(me.data.status !== "A");
        me.setWatchers(me.data.subscribers || []);
        //
        me.setRootButton.setDisabled(me.data.status !== "A");
        // Install plugins
        if(data.plugins && !me.plugins.length) {
            Ext.each(data.plugins, function(v) {
                var cls = v[0],
                    config = {
                        app: me.app
                    },
                    p;
                Ext.apply(config, v[1]);
                p = Ext.create(cls, config);
                me.plugins.push(p);
                me.tabPanel.add(p);
            });
        }
        // Update plugins content
        if(me.plugins.length) {
            Ext.each(me.plugins, function(p) {
                p.updateData(data);
            });
        }
        //
        if(oldId !== me.data.id) {
            me.messageField.setValue("");
            // @todo: Fix, doesn't work
            me.tabPanel.setActiveTab(me.overviewPanel);
        }
    },
    //
    onClose: function() {
        var me = this;
        // Remove plugins
        if(me.plugins.length) {
            Ext.each(me.plugins, function(p) {
                me.tabPanel.remove(p);
            });
            me.plugins = [];
        }
        //
        me.app.showGrid();
    },
    //
    onMessageKey: function(field, key) {
        var me = this;
        switch(key.getKey()) {
            case Ext.EventObject.ENTER:
                key.stopEvent();
                me.submitMessage(me.messageField.getValue());
                break;
            case Ext.EventObject.ESC:
                key.stopEvent();
                field.setValue("");
                break;
        }
    },
    //
    submitMessage: function(msg) {
        var me = this;
        if(!msg)
            return;
        Ext.Ajax.request({
            url: "/fm/alarm/" + me.data.id + "/post/",
            method: "POST",
            jsonData: {
                msg: msg
            },
            success: function(response) {
                me.messageField.setValue("");
                me.logStore.add({
                    timestamp: new Date(),
                    from_status: me.data.status,
                    to_status: me.data.status,
                    message: msg
                });
            },
            failure: function() {
                NOC.error("Failed to post message");
            }
        });
    },
    //
    onRefresh: function() {
        var me = this;
        me.showAlarm(me.data.id);
    },
    //
    setWatchers: function(watchers) {
        var me = this,
            is_watcher = false,
            msg = watchers.map(function(v) {
                if(v.login === NOC.username) {
                    is_watcher = true;
                }
                return v.name + " (" + v.login + ")";
            }).join(", ");
        // me.watchersField.setValue(msg);
        me.watchButton.setIconCls(
            is_watcher? "icon_star" : "icon_star_grey"
        );
        me.watchButton.toggle(is_watcher);
    },
    //
    onClear: function() {
        var me = this;
        Ext.Msg.show({
            title: "Clear alarm?",
            msg: "Please confirm the alarm is closed and must be cleared?",
            buttons: Ext.Msg.YESNO,
            icon: Ext.Msg.QUESTION,
            fn: function(btn) {
                if(btn == "yes") {
                    Ext.Ajax.request({
                        url: "/fm/alarm/" + me.data.id + "/clear/",
                        method: "POST",
                        scope: me,
                        success: function() {
                            me.onRefresh()
                        },
                        failure: function() {
                            NOC.error("Failed to clear alarm");
                        }
                    });
                }
            }
        });
    },
    //
    onWatch: function() {
        var me = this,
            cmd = me.watchButton.pressed? "/subscribe/" : "/unsubscribe/";
        Ext.Ajax.request({
            url: "/fm/alarm/" + me.data.id + cmd,
            method: "POST",
            scope: me,
            success: function(response) {
                var watchers = Ext.decode(response.responseText);
                me.setWatchers(watchers);
            },
            failure: function() {
                NOC.error("Failed to set watcher");
            }
        })

    },
    //
    onSetRoot: function() {
        var me = this;
        Ext.Msg.prompt(
            "Set root cause",
            "Please enter root cause alarm id",
            function(btn, text) {
                if(btn == "ok") {
                    // @todo: Check alarm id
                    Ext.Ajax.request({
                        url: "/fm/alarm/" + me.data.id + "/set_root/",
                        method: "POST",
                        jsonData: {
                            root: text
                        },
                        success: function() {
                            me.onRefresh();
                        },
                        failure: function() {
                            NOC.error("Failed to set root cause");
                        }
                    });
                }
            }
        );
    },

    onShowMap: function() {
        var me = this;
        NOC.launch("inv.map", "history", {
            args: [me.data.segment_id]
        });
    },

    onShowObject: function() {
        var me = this;
        NOC.launch(
            "sa.managedobject",
            "history",
            {args: [me.data.managed_object]}
        );
    }
});
