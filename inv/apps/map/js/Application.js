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

        me.readOnly = !me.hasPermission("write");

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

        me.editButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.edit,
            text: "Edit",
            enableToggle: true,
            disabled: true,
            tooltip: "Edit map",
            scope: me,
            handler: me.onEdit
        });

        me.saveButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.save,
            text: "Save",
            disabled: true,
            scope: me,
            handler: me.onSave
        });

        me.revertButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.undo,
            text: "Revert",
            disabled: true,
            scope: me,
            handler: me.onRevert
        });

        me.segmentInspector = Ext.create(
            "NOC.inv.map.inspectors.SegmentInspector",
            {
                app: me,
                readOnly: me.readOnly
            }
        );

        me.managedObjectInspector = Ext.create(
            "NOC.inv.map.inspectors.ManagedObjectInspector",
            {
                app: me,
                readOnly: me.readOnly
            }
        );

        me.linkInspector = Ext.create(
            "NOC.inv.map.inspectors.LinkInspector",
            {
                app: me,
                readOnly: me.readOnly
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
            readOnly: me.readOnly,
            listeners: {
                scope: me,
                mapready: me.onMapReady,
                changed: me.onChanged
            }
        });

        me.viewMapButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.globe,
            tooltip: "Show static map",
            enableToggle: true,
            toggleGroup: "overlay",
            pressed: true,
            scope: me,
            handler: me.onSetOverlay,
            mapOverlay: me.mapPanel.LO_NONE
        });

        me.viewLoadButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.line_chart,
            tooltip: "Show interface load",
            enableToggle: true,
            toggleGroup: "overlay",
            scope: me,
            handler: me.onSetOverlay,
            mapOverlay: me.mapPanel.LO_LOAD
        });


        Ext.apply(me, {
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        me.segmentCombo,
                        me.editButton,
                        me.saveButton,
                        me.revertButton,
                        "-",
                        me.viewMapButton,
                        me.viewLoadButton
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
        // @todo: Restrict to permissions
        me.editButton.setDisabled(me.readOnly);
        me.editButton.setPressed(false);
        me.saveButton.setDisabled(true);
        me.revertButton.setDisabled(true);
        me.inspectSegment();
        me.viewMapButton.setPressed(true);
    },

    onMapReady: function() {
        var me = this;
        me.segmentCombo.setDisabled(false);
        if(me.getCmd() === "history") {
            me.loadSegment(me.noc.cmd.args[0]);
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
    },

    onEdit: function() {
        var me = this;
        me.mapPanel.setInteractive(me.editButton.pressed);
    },

    onSave: function() {
        var me = this;
        me.mapPanel.save();
    },

    onRevert: function() {
        var me = this;
        me.loadSegment(me.currentSegmentId);
    },

    onChanged: function() {
        var me = this;
        me.saveButton.setDisabled(me.readOnly);
        me.revertButton.setDisabled(me.readOnly);
    },

    onCloseApp: function() {
        var me = this;
        me.mapPanel.stopPolling();
    },

    onSetOverlay: function(button) {
        var me = this;
        me.mapPanel.setOverlayMode(button.mapOverlay);
    }
});
