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

    initComponent: function() {
        var me = this;

        me.overviewPanel = Ext.create("Ext.panel.Panel", {
            title: "Overview"
        });

        me.helpPanel = Ext.create("Ext.panel.Panel", {
            title: "Help"
        });

        me.dataPanel = Ext.create("Ext.panel.Panel", {
            title: "Data"
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

        me.tabPanel = Ext.create("Ext.tab.Panel", {
            items: [
                me.overviewPanel,
                me.helpPanel,
                me.dataPanel,
                me.logPanel
            ]
        });


        Ext.apply(me, {
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        {
                            text: "Close",
                            iconCls: "icon_arrow_undo",
                            scope: me,
                            handler: me.onClose
                        }
                    ]
                }
            ],
            items: [
                me.tabPanel
            ]
        });
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
            panel.update(template(data));
        }
    },
    //
    updateData: function(data) {
        var me = this,
            oldId = me.data ? me.data.id : undefined;
        me.data = data;
        me.setTitle(
            Ext.String.format("Event {0}: {1}", data.id, data.subject)
        );
        me.updatePanel(me.overviewPanel, me.app.templates.Overview,
            data.subject, data);
        me.updatePanel(me.helpPanel, me.app.templates.Help,
            data.symptoms, data);
        me.updatePanel(me.dataPanel, me.app.templates.Data,
            data.vars.length || data.raw_vars.length || data.resolved_vars.length, data);
        me.logStore.loadData(data.log || []);
        if(oldId !== me.data.id) {
            me.messageField.setValue("");
            me.tabPanel.setActiveTab(0);
        }
    },
    //
    onClose: function() {
        var me = this;
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
    }
});
