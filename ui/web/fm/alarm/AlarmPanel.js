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
            fieldLabel: __("ID"),
            labelWidth: 20,
            width: 190,
            labelClsExtra: "noc-label-required"
        });

        me.topPanel = Ext.create("Ext.panel.Panel", {
            layout: "fit",
            bodyPadding: 4,
            tpl: "<div class='noc-alarm-subject {row_class}'>{subject} [{severity__label}/{severity}]"
            + "  <span class='noc-alarm-timestamp'>{timestamp} ({duration})</span>"
            + "</div>"
            + "<div>"
            + "<span class='noc-alarm-label'>Object</span> {managed_object__label} "
            + "<span class='noc-alarm-label'>IP</span> {managed_object_address} "
            + "<tpl if='managed_object_platform'><span class='noc-alarm-label'>Platform</span> {managed_object_platform} </tpl>"
            + "<tpl if='managed_object_version'><span class='noc-alarm-label'>Version</span> {managed_object_version} </tpl>"
            + "</div>"
            + "<tpl if='segment_path'><div><span class='noc-alarm-label'>Segment</span> {segment_path}"
            + "</div></tpl>"
            + "<tpl if='container_path'><div><span class='noc-alarm-label'>Location</span> {container_path}"
            + "</div></tpl>"
            + "<tpl if='address_path'><div><span class='noc-alarm-label'>Address</span> {address_path}"
            + "</div></tpl>"
        });

        me.overviewPanel = Ext.create("Ext.panel.Panel", {
            title: __("Overview"),
            scrollable: true,
            tpl: '<div class="noc-tp"><b>{subject}</b><br/><pre>{body}</pre></div>'
        });

        me.helpPanel = Ext.create("Ext.panel.Panel", {
            title: __("Help"),
            scrollable: true,
            tpl: '<div class="noc-tp"><b>Symptoms:</b><br/><pre>{symptoms}</pre><br/><b>Probable Causes:</b><br/><pre>{probable_causes}</pre><br/><b>Recommended Actions:</b><br/><pre>{recommended_actions}</pre><br/></div>'
        });

        me.dataPanel = Ext.create("Ext.panel.Panel", {
            title: __("Data"),
            scrollable: true,
            tpl: '<div class="noc-tp">\n    <table border="0">\n        <tpl if="vars && vars.length">\n            <tr>\n                <th colspan="2">Alarm Variables</th>\n            </tr>\n            <tpl foreach="vars">\n                <tpl foreach=".">\n                    <tr>\n                        <td><b>{$}</b></td>\n                        <td>{.}</td>\n                    </tr>\n                </tpl>\n            </tpl>\n        </tpl>\n        <tpl if="resolved_vars && resolved_vars.length">\n            <tr>\n                <th colspan="2">Resolved Variables</th>\n            </tr>\n            <tpl foreach="resolved_vars">\n                <tpl foreach=".">\n                    <tr>\n                        <td><b>{$}</b></td>\n                        <td>{.}</td>\n                    </tr>\n                </tpl>\n            </tpl>\n        </tpl>\n        <tpl if="raw_vars && raw_vars.length">\n            <tr>\n                <th colspan="2">Raw Variables</th>\n            </tr>\n            <tpl foreach="raw_vars">\n                <tpl foreach=".">\n                    <tr>\n                        <td><b>{$}</b></td>\n                        <td>{.}</td>\n                    </tr>\n                </tpl>\n            </tpl>\n        </tpl>\n    </table>\n</div>'
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
            fieldLabel: __("New message"),
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
            title: __("Log"),
            store: me.logStore,
            autoScroll: true,
            columns: [
                {
                    dataIndex: "timestamp",
                    text: __("Time"),
                    renderer: NOC.render.DateTime,
                    width: 120
                },
                {
                    dataIndex: "from_status",
                    text: __("From"),
                    renderer: NOC.render.Choices(me.app.STATUS_MAP),
                    width: 50
                },
                {
                    dataIndex: "to_status",
                    text: __("To"),
                    renderer: NOC.render.Choices(me.app.STATUS_MAP),
                    width: 50
                },
                {
                    dataIndex: "message",
                    text: __("Message"),
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
            title: __("Events"),
            store: me.eventsStore,
            autoScroll: true,
            columns: [
                {
                    dataIndex: "id",
                    text: __("ID"),
                    width: 150
                },
                {
                    dataIndex: "timestamp",
                    text: __("Time"),
                    renderer: NOC.render.DateTime,
                    width: 120
                },
                {
                    dataIndex: "event_class",
                    text: __("Class"),
                    renderer: NOC.render.Lookup("event_class"),
                    width: 200
                },
                {
                    dataIndex: "subject",
                    text: __("Subject"),
                    flex: 1
                }
            ]
        });
        // Alarms
        me.defaultRoot = {
            text: __("."),
            children: []
        };

        me.alarmsStore = Ext.create("Ext.data.TreeStore", {
            model: "NOC.fm.alarm.AlarmsModel",
            root: me.defaultRoot
        });
        me.alarmsPanel = Ext.create("Ext.tree.Panel", {
            title: __("Alarms"),
            store: me.alarmsStore,
            rootVisible: false,
            useArrows: true,
            columns: [
                {
                    xtype: "treecolumn",
                    dataIndex: "id",
                    text: __("ID"),
                    width: 200
                },
                {
                    dataIndex: "timestamp",
                    text: __("Time"),
                    width: 120,
                    renderer: NOC.render.DateTime
                },
                {
                    dataIndex: "managed_object",
                    text: __("Object"),
                    width: 200,
                    renderer: NOC.render.Lookup("managed_object")
                },
                {
                    dataIndex: "alarm_class",
                    text: __("Class"),
                    renderer: NOC.render.Lookup("alarm_class")
                },
                {
                    dataIndex: "subject",
                    text: __("Subject"),
                    flex: 1
                }
            ],
            viewConfig: {
                getRowClass: function(record, index, params, store) {
                    var c = record.get("row_class");
                    return c ? c : "";
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
            text: __("Clear"),
            glyph: NOC.glyph.eraser,
            scope: me,
            handler: me.onClear
        });

        me.watchButton = Ext.create("Ext.Button", {
            text: __("Watch"),
            enableToggle: true,
            glyph: NOC.glyph.star,
            scope: me,
            handler: me.onWatch
        });

        me.setRootButton = Ext.create("Ext.Button", {
            text: __("Set Root Cause"),
            glyph: NOC.glyph.paperclip,
            scope: me,
            handler: me.onSetRoot
        });

        me.showMapButton = Ext.create("Ext.button.Button", {
            text: __("Show Map"),
            glyph: NOC.glyph.globe,
            scope: me,
            handler: me.onShowMap
        });

        me.showObjectButton = Ext.create("Ext.button.Button", {
            text: __("Show Object"),
            glyph: NOC.glyph.eye,
            scope: me,
            handler: me.onShowObject
        });

        me.escalateButton = Ext.create("Ext.button.Button", {
            text: __("Escalate"),
            glyph: NOC.glyph.ambulance,
            tooltip: __('Escalate'),
            scope: me,
            handler: me.onEscalateObject
        });

        me.showAlarmCardButton = Ext.create("Ext.button.Button", {
            text: __("Card"),
            glyph: NOC.glyph.eye,
            scope: me,
            handler: me.onShowCard
        });

        Ext.apply(me, {
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        {
                            text: __("Close"),
                            glyph: NOC.glyph.arrow_left,
                            scope: me,
                            handler: me.onClose
                        },
                        {
                            text: __("Refresh"),
                            glyph: NOC.glyph.refresh,
                            scope: me,
                            handler: me.onRefresh
                        },
                        "-",
                        me.escalateButton,
                        me.showAlarmCardButton,
                        me.showMapButton,
                        me.showObjectButton,
                        "-",
                        me.clearButton,
                        me.watchButton,
                        me.setRootButton,
                        "->",
                        me.alarmIdField
                    ]
                }
            ],
            items: [
                me.topPanel,
                {
                    xtype: 'splitter'
                },
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
                NOC.error(__("Failed to get alarm"));
            }
        });
        me.app.setHistoryHash(alarmId);
    },
    //
    updatePanel: function(panel, enabled, data) {
        panel.setDisabled(!enabled);
        panel.setVisible(enabled);
        if(enabled) {
            panel.update(data);
        }
    },
    //
    updateData: function(data) {
        var me = this,
            oldId = me.data ? me.data.id : undefined;

        me.data = data;
        //
        me.alarmIdField.setValue(me.data.id);
        me.topPanel.setData(me.data);
        //
        me.updatePanel(me.overviewPanel, data.subject, data);
        me.updatePanel(me.helpPanel, data.symptoms, data);
        me.updatePanel(me.dataPanel,
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
        me.escalateButton.setDisabled(me.data.status === "C");
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
                NOC.error(__("Failed to post message"));
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
            is_watcher ? "icon_star" : "icon_star_grey"
        );
        me.watchButton.toggle(is_watcher);
    },
    //
    onClear: function() {
        var me = this;
        Ext.Msg.show({
            title: __("Clear alarm?"),
            msg: __("Please confirm the alarm is closed and must be cleared?"),
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
                            NOC.error(__("Failed to clear alarm"));
                        }
                    });
                }
            }
        });
    },
    //
    onWatch: function() {
        var me = this,
            cmd = me.watchButton.pressed ? "/subscribe/" : "/unsubscribe/";
        Ext.Ajax.request({
            url: "/fm/alarm/" + me.data.id + cmd,
            method: "POST",
            scope: me,
            success: function(response) {
                var watchers = Ext.decode(response.responseText);
                me.setWatchers(watchers);
            },
            failure: function() {
                NOC.error(__("Failed to set watcher"));
            }
        })

    },
    //
    onSetRoot: function() {
        var me = this;
        Ext.Msg.prompt(
            __("Set root cause"),
            __("Please enter root cause alarm id"),
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
                            NOC.error(__("Failed to set root cause"));
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
        NOC.launch("sa.managedobject", "history", {
            args: [me.data.managed_object]
        });

    },
    onEscalateObject: function() {
        var me = this;

        Ext.Ajax.request({
            url: "/fm/alarm/" + me.data.id + "/escalate/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);

                if(data.status) {
                    NOC.info(_('Escalated'));
                } else {
                    NOC.error(__("Escalate failed : ") + (data.hasOwnProperty('error') ? data.error : 'unknowns error!'));
                }
            },
            failure: function() {
                NOC.error(__("Escalate failed"));
            }
        });
    },
    onShowCard: function() {
        var me = this;
        window.open(
            "/api/card/view/alarm/" + me.data.id + "/"
        );
    }
});
