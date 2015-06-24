//---------------------------------------------------------------------
// inv.map application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.map.Application");

Ext.define("NOC.inv.map.Application", {
    extend: "NOC.core.Application",
    requires: [
        "NOC.inv.networksegment.LookupField",
        "NOC.inv.map.MapPanel"
    ],

    initComponent: function() {
        var me = this;

        me.segmentCombo = Ext.create("NOC.inv.networksegment.LookupField", {
            fieldLabel: "Segment",
            labelWidth: 45,
            minWidth: 280,
            allowBlank: true,
            disabled: true,
            emptyText: "Select segment...",
            listeners: {
                scope: me,
                select: me.onSelectSegment
            }
        });

        me.segmentInspector = Ext.create(
            "NOC.inv.map.inspectors.SegmentInspector",
            {
                app: me
            }
        );

        me.managedObjectInspector = Ext.create(
            "NOC.inv.map.inspectors.ManagedObjectInspector",
            {
                app: me
            }
        );

        me.linkInspector = Ext.create(
            "NOC.inv.map.inspectors.LinkInspector",
            {
                app: me
            }
        );

        me.inspectorPanel = Ext.create("Ext.panel.Panel", {
            app: me,
            layout: "card",
            autoScroll: true,
            items: [
                me.segmentInspector,
                me.managedObjectInspector,
                me.linkInspector
            ],
            dock: "right",
            width: 200
        });

        me.mapPanel = Ext.create("NOC.inv.map.MapPanel", {
            app: me,
            listeners: {
                scope: me,
                mapready: me.onMapReady
            }
        });

        Ext.apply(me, {
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        me.segmentCombo
                    ]
                },
                me.inspectorPanel
            ],
            items: [me.mapPanel]
        });
        me.callParent();
    },

    loadSegment: function(segmentId) {
        var me = this;
        me.segmentCombo.setDisabled(false);
        me.segmentCombo.setValue(segmentId);
        me.setHistoryHash(segmentId);
        // @todo: Remove
        me.mapPanel.loadSegment(segmentId);
        me.currentSegmentId = segmentId;
        me.inspectSegment();
    },

    onMapReady: function() {
        var me = this,
            segmentId;
        me.segmentCombo.setDisabled(false);
        if(me.getCmd() === "history") {
            me.loadSegment(me.noc.cmd.args);
        }
    },

    onSelectSegment: function(combo, record, opts) {
        var me = this;
        me.loadSegment(record.get("id"));
    },

    inspectSegment: function() {
        var me = this;
        me.inspectorPanel.getLayout().setActiveItem(
            me.segmentInspector
        );
        if(me.currentSegmentId) {
            me.segmentInspector.preview(me.currentSegmentId);
        }
    },

    inspectManagedObject: function(objectId) {
        var me = this;
        me.inspectorPanel.getLayout().setActiveItem(
            me.managedObjectInspector
        );
        me.managedObjectInspector.preview(me.currentSegmentId, objectId);
    },

    inspectLink: function(linkId) {
        var me = this;
        me.inspectorPanel.getLayout().setActiveItem(
            me.linkInspector
        );
        me.linkInspector.preview(me.currentSegmentId, linkId);
    }

});
