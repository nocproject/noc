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


    zoomLevels: [
        [0.25, "25%"],
        [0.5, "50%"],
        [0.75, "75%"],
        [1.0, "100%"],
        [1.25, "125%"],
        [1.5, "150%"],
        [2.0, "200%"],
        [3.0, "300%"],
        [4.0, "400%"]
    ],

    initComponent: function() {
        var me = this;

        me.readOnly = !me.hasPermission("write");

        me.segmentCombo = Ext.create("NOC.inv.networksegment.LookupField", {
            fieldLabel: __("Segment"),
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

        me.zoomCombo = Ext.create("Ext.form.ComboBox", {
            store: me.zoomLevels,
            width: 60,
            value: 1.0,
            valueField: "zoom",
            displayField: "label",
            listeners: {
                scope: me,
                select: me.onZoom
            }
        });

        me.reloadButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.refresh,
            text: __("Reload"),
            scope: me,
            handler: me.onReload
        });

        me.editButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.edit,
            text: __("Edit"),
            enableToggle: true,
            disabled: true,
            tooltip: __("Edit map"),
            scope: me,
            handler: me.onEdit
        });

        me.saveButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.save,
            text: __("Save"),
            disabled: true,
            scope: me,
            handler: me.onSave
        });

        me.revertButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.undo,
            text: __("Revert"),
            disabled: true,
            scope: me,
            handler: me.onRevert
        });

        me.newLayoutButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.repeat,
            text: __("New layout"),
            disabled: me.readOnly,
            scope: me,
            handler: me.onNewLayout
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
            tooltip: __("Show static map"),
            enableToggle: true,
            toggleGroup: "overlay",
            pressed: true,
            scope: me,
            handler: me.onSetOverlay,
            mapOverlay: me.mapPanel.LO_NONE
        });

        me.viewLoadButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.line_chart,
            tooltip: __("Show interface load"),
            enableToggle: true,
            toggleGroup: "overlay",
            scope: me,
            handler: me.onSetOverlay,
            mapOverlay: me.mapPanel.LO_LOAD
        });

        me.viewStpButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.edit,
            text: __("STP"),
            enableToggle: true,
            disabled: true,
            tooltip: __("Show STP topology"),
            scope: me,
            handler: me.onStp
        });

        Ext.apply(me, {
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        me.segmentCombo,
                        "-",
                        me.zoomCombo,
                        me.reloadButton,
                        "-",
                        me.editButton,
                        me.saveButton,
                        me.revertButton,
                        me.newLayoutButton,
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
        me.zoomCombo.setValue(1.0);
        me.mapPanel.setZoom(1.0);
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

    onZoom: function(combo, record, opts) {
        var me = this;
        me.mapPanel.setZoom(record.get("field1"));
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
        if(me.editButton.pressed) {
            me.mapPanel.setOverlayMode(0);
            me.viewMapButton.setPressed(true);
        }
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

    onReload: function() {
        var me = this;
        me.loadSegment(me.currentSegmentId);
    },

    onChanged: function() {
        var me = this;
        if(me.editButton.pressed) {
            me.saveButton.setDisabled(me.readOnly);
            me.revertButton.setDisabled(me.readOnly);
        }
    },

    onCloseApp: function() {
        var me = this;
        me.mapPanel.stopPolling();
    },

    onSetOverlay: function(button) {
        var me = this;
        me.mapPanel.setOverlayMode(button.mapOverlay);
    },

    onNewLayout: function(btn, ev) {
        var me = this,
            forceSpring = ev.shiftKey;
        console.log(arguments);
        Ext.Msg.show({
            title: __("Reset Layout"),
            message: __("Would you like to reset current layout and generate new?"),
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            fn: function(btn) {
                if(btn == "yes") {
                    me.mapPanel.resetLayout(forceSpring);
                }
            }
        });
    },

    onStp: function() {
        var me = this;
        me.mapPanel.setStp(me.viewStpButton.pressed);
    }
});
