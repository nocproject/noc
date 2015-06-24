//---------------------------------------------------------------------
// Managed object inspector
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.map.inspectors.ManagedObjectInspector");

Ext.define("NOC.inv.map.inspectors.ManagedObjectInspector", {
    extend: "Ext.panel.Panel",
    title: "Object Inspector",
    autoScroll: true,

    initComponent: function() {
        var me = this;
        me.infoText = Ext.create("Ext.container.Container", {
            padding: 4
        });

        me.lookButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.eye,
            scope: me,
            tooltip: "Look details",
            handler: me.onLook,
            disabled: true
        });

        me.segmentButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.location_arrow,
            scope: me,
            tooltip: "Jump to Segment",
            handler: me.onJumpSegment,
            disabled: true
        });

        Ext.apply(me, {
            items: [
                me.infoText
            ],
            dockedItems: [{
                xtype: "toolbar",
                dock: "top",
                items: [
                    me.lookButton,
                    me.segmentButton
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
    }
});