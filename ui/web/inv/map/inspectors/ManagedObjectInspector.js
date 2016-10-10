//---------------------------------------------------------------------
// Managed object inspector
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.map.inspectors.ManagedObjectInspector");

Ext.define("NOC.inv.map.inspectors.ManagedObjectInspector", {
    extend: "Ext.panel.Panel",
    title: __("Object Inspector"),
    autoScroll: true,
    bodyStyle: {
        background: "#c0c0c0"
    },

    initComponent: function() {
        var me = this;

        me.infoText = Ext.create("Ext.container.Container", {
            padding: 4,
            region: 'north'
        });

        me.legend = Ext.create('NOC.inv.map.Legend', {
            width: me.width
        });

        // autoShow: false doesn't work
        me.legend.hide();

        me.lookButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.pencil,
            scope: me,
            tooltip: __("Edit"),
            handler: me.onLook,
            disabled: true
        });

        me.cardButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.eye,
            scope: me,
            tooltip: __("View card"),
            handler: me.onMOCard,
            disabled: true
        });

        me.segmentButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.location_arrow,
            scope: me,
            tooltip: __("Jump to Segment"),
            handler: me.onJumpSegment,
            disabled: true
        });

        me.dashboardButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.line_chart,
            scope: me,
            tooltip: __("Show dashboard"),
            handler: me.onDashboard,
            disabled: true
        });

        me.consoleButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.terminal,
            scope: me,
            tooltip: __("Console"),
            handler: me.onConsole,
            disabled: true
        });

        Ext.apply(me, {
            layout: 'border',
            items: [
                me.infoText,
                me.legend
            ],
            dockedItems: [{
                xtype: "toolbar",
                dock: "top",
                items: [
                    me.cardButton,
                    me.lookButton,
                    me.segmentButton,
                    me.dashboardButton,
                    me.consoleButton
                ]
            }]
        });
        me.callParent();
    },

    preview: function(segmentId, objectId) {
        var me = this;
        Ext.Ajax.request({
            url: "/inv/map/" + segmentId + "/info/managedobject/" + objectId + "/",
            method: "GET",
            scope: me,
            mask: me,
            success: function(response) {
                me.applyData(Ext.decode(response.responseText))
            }
        });
    },

    applyData: function(data) {
        var me = this,
            t;

        t = "<b>Name:</b> " + Ext.htmlEncode(data.name);
        t += "<br><b>Address:</b> " + data.address;
        t += "<br><b>Profile:</b> " + Ext.htmlEncode(data.profile);
        if(data.platform && data.platform.length) {
            t += "<br><b>Platform:</b> " + Ext.htmlEncode(data.platform);
        }
        if(data.external) {
            t += "<br><b>Segment:</b> " + Ext.htmlEncode(data.external_segment.name);
            me.externalSegmentId = data.external_segment.id;
            me.segmentButton.setDisabled(false);
        } else {
            me.externalSegmentId = null;
            me.segmentButton.setDisabled(true);
        }
        if(data.description && data.description.length) {
            t += "<br><b>Description:</b><br>" + Ext.htmlEncode(data.description);
        }
        me.infoText.setHtml(t);
        me.currentObjectId = data.id;
        me.lookButton.setDisabled(false);
        me.cardButton.setDisabled(false);
        me.dashboardButton.setDisabled(false);
        me.consoleButton.setDisabled(false);
        me.consoleUrl = data.console_url;
    },

    onLook: function() {
        var me = this;
        if(me.currentObjectId) {
            NOC.launch("sa.managedobject", "history", {args: [me.currentObjectId]});
        }
    },

    onJumpSegment: function() {
        var me = this;
        me.app.loadSegment(me.externalSegmentId);
    },

    onMOCard: function() {
        var me = this;
        if(me.currentObjectId) {
            window.open(
                "/api/card/view/managedobject/" + me.currentObjectId + "/"
            );
        }
    },

    onDashboard: function() {
        var me = this;
        if(me.currentObjectId) {
            window.open(
                "/ui/grafana/dashboard/script/noc.js?dashboard=mo&id=" + me.currentObjectId
            );
        }
    },

    onConsole: function() {
        var me = this;
        window.open(me.consoleUrl);
    },

    onLegend: function() {
        if(this.legend.isVisible()) {
            this.legend.hide();
        } else {
            this.legend.show()
        }
    }
});