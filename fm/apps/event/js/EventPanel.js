//---------------------------------------------------------------------
// fm.event application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.event.EventPanel");

Ext.define("NOC.fm.event.EventPanel", {
    extend: "Ext.panel.Panel",
    app: null,
    autoScroll: true,
    layout: {
        type: "vbox",
        pack: "start",
        align: "stretch"
    },

    initComponent: function() {
        var me = this,
            lw = 50;

        me.eventIdField = Ext.create("Ext.form.DisplayField", {
            fieldLabel: "ID",
            labelWidth: 20,
            width: 190,
            labelClsExtra: "noc-label-required"
        });

        me.subjectField = Ext.create("Ext.form.DisplayField", {
            fieldLabel: "Event",
            labelWidth: lw
        });

        me.objectField = Ext.create("Ext.form.DisplayField", {
            fieldLabel: "Object",
            labelWidth: lw
        });

        me.eventClassField = Ext.create("Ext.form.DisplayField", {
            fieldLabel: "Class",
            labelWidth: lw
        });

        me.timeField = Ext.create("Ext.form.DisplayField", {
            fieldLabel: "Time",
            labelWidth: lw
        });

        me.topPanel = Ext.create("Ext.panel.Panel", {
            height: 98,
            bodyPadding: 4,
            layout: {
                type: "vbox",
                align: "stretch",
                pack: "start"
            },
            defaults: {
                labelClsExtra: "noc-label-required"
            },
            items: [
                me.subjectField,
                me.objectField,
                me.eventClassField,
                me.timeField
            ]
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
        // Alarms
        me.alarmsStore = Ext.create("Ext.data.Store", {
            fields: [
                {
                    name: "timestamp",
                    type: "date"
                },
                "id", "status", "role", "alarm_class",
                "alarm_class__label", "subject"
            ],
            data: []
        });
        me.alarmsPanel = Ext.create("Ext.grid.Panel", {
            title: "Alarms",
            store: me.alarmsStore,
            autoScroll: true,
            columns: [
                {
                    dataIndex: "id",
                    text: "ID",
                    width: 200
                },
                {
                    dataIndex: "timestamp",
                    text: "Time",
                    renderer: NOC.render.DateTime,
                    width: 120
                },
                {
                    dataIndex: "role",
                    text: "Event Role",
                    renderer: NOC.render.Choices({
                        O: "Opening",
                        C: "Closing"
                    }),
                    width: 70
                },
                {
                    dataIndex: "status",
                    text: "Alrm Status",
                    renderer: NOC.render.Choices({
                        A: "Active",
                        C: "Closed"
                    }),
                    width: 70
                },
                {
                    dataIndex: "alarm_class",
                    text: "Class",
                    renderer: NOC.render.Lookup("alarm_class"),
                    width: 250
                },
                {
                    dataIndex: "subject",
                    text: "Subject",
                    flex: 1
                }
            ]
        });
        //
        me.tabPanel = Ext.create("Ext.tab.Panel", {
            flex: 1,
            items: [
                me.overviewPanel,
                me.helpPanel,
                me.dataPanel,
                me.logPanel,
                me.alarmsPanel
            ]
        });

        me.reclassifyButton = Ext.create("Ext.button.Button", {
            text: "Reclassify",
            glyph: NOC.glyph.repeat,
            scope: me,
            handler: me.onReclassify
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
                        me.reclassifyButton,
                        "-",
                        {
                            text: "JSON",
                            glyph: NOC.glyph.file,
                            scope: me,
                            handler: me.onJSON
                        },
                        "->",
                        me.eventIdField
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
    showEvent: function(eventId) {
        var me = this;
        Ext.Ajax.request({
            url: "/fm/event/" + eventId + "/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                me.updateData(data);
            },
            failure: function() {
                NOC.error("Failed to get event");
            }
        });
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
        me.eventIdField.setValue(me.data.id);
        //
        me.subjectField.setValue(
            Ext.String.format("{0} [{1}]",
                me.data.subject ? me.data.subject : "Unclassified event",
                me.app.STATUS_MAP[me.data.status]
            )
        );
        // Managed object details
        if(me.data.managed_object_address) {
            o.push(me.data.managed_object_address);
        }
        o.push(me.data.managed_object_profile);
        if(me.data.managed_object_platform) {
            o.push(me.data.managed_object_platform);
        }
        if(me.data.managed_object_version) {
            o.push(me.data.managed_object_version);
        }
        me.objectField.setValue(me.data.managed_object__label + " (" + o.join(", ") + ")");
        me.eventClassField.setValue(me.data.event_class__label);
        me.timeField.setValue(me.data.timestamp);
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
        me.alarmsPanel.setDisabled(!data.alarms || !data.alarms.length);
        me.alarmsStore.loadData(data.alarms || []);
        //
        me.reclassifyButton.setDisabled(
            data.status == "N" || data.status === "F"
        );
        //
        if(oldId !== me.data.id) {
            me.messageField.setValue("");
            // @todo: Fix, doesn't work
            me.tabPanel.setActiveTab(me.overviewPanel);
        }
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
            url: "/fm/event/" + me.data.id + "/post/",
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
    onJSON: function() {
        var me = this;
        me.app.showItem(me.app.ITEM_JSON);
        me.app.jsonPanel.preview({
            data: me.data
        });
    },
    //
    onRefresh: function() {
        var me = this;
        me.showEvent(me.data.id);
    },
    //
    onReclassify: function() {
        var me = this;
        Ext.Ajax.request({
            url: "/fm/event/" + me.data.id + "/reclassify/",
            method: "POST",
            scope: me,
            success: function(response) {
                me.showEvent(me.data.id);
            },
            failure: function() {
                NOC.error("Failed to reclassify");
            }
        });
    }
});
