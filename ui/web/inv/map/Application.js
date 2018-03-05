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
        "NOC.inv.networksegment.TreeCombo",
        "NOC.inv.map.MapPanel"
    ],
    rightWidth: 200,
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

        me.segmentCombo = Ext.create('NOC.inv.networksegment.TreeCombo', {
            fieldLabel: __("Segment"),
            labelWidth: 50,
            labelAlign: "left",
            listAlign: "left",
            minWidth: 400,
            emptyText: __("Select segment..."),
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
            tooltip: __("Reload"),
            scope: me,
            handler: me.onReload
        });

        me.editButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.edit,
            enableToggle: true,
            disabled: true,
            tooltip: __("Edit map"),
            scope: me,
            handler: me.onEdit
        });

        me.rotateButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.rotate_right,
            tooltip: __("Rotate"),
            disabled: true,
            scope: me,
            handler: me.onRotate
        });

        me.saveButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.save,
            tooltip: __("Save"),
            disabled: true,
            scope: me,
            handler: me.onSave
        });

        me.revertButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.undo,
            tooltip: __("Revert"),
            disabled: true,
            scope: me,
            handler: me.onRevert
        });

        me.newLayoutButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.medkit,
            tooltip: __("New layout"),
            disabled: me.readOnly,
            scope: me,
            handler: me.onNewLayout
        });

        me.addressIPButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.tag,
            tooltip: __("Name/IP device"),
            enableToggle: true,
            // disabled: me.readOnly,
            scope: me,
            handler: me.onChangeName
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

        me.cloudInspector = Ext.create(
            "NOC.inv.map.inspectors.CloudInspector",
            {
                app: me,
                readOnly: me.readOnly
            }
        );

        me.legendPanel = Ext.create("NOC.inv.map.Legend", {
            collapsed: true,
            region: 'south',
            width: this.rightWidth,
            collapsible: true,
            collapseMode: undefined,
            header: false,
            hideCollapseTool: true
        });

        me.miniMapPanel = Ext.create("NOC.inv.map.MiniMap", {
            region: 'south',
            width: this.rightWidth,
            collapsible: true,
            collapseMode: undefined,
            header: false,
            hideCollapseTool: true
        });

        me.basketPanel = Ext.create("NOC.inv.map.Basket", {
            collapsed: true,
            region: 'south',
            width: this.rightWidth,
            collapsible: true,
            collapseMode: undefined,
            header: false,
            hideCollapseTool: true,
            listeners: {
                scope: me,
                createmaintaince: function(data) {
                    me.mapPanel.newMaintaince(data.items);
                },
                addtomaintaince: function(data) {
                    me.mapPanel.addToMaintaince(data.items)
                }
            }
        });

        me.inspectorPanel = Ext.create("Ext.panel.Panel", {
            app: me,
            layout: "card",
            region: "center",
            scrollable: true,
            items: [
                me.segmentInspector,
                me.managedObjectInspector,
                me.linkInspector
            ]
        });

        me.rightPanel = Ext.create("Ext.panel.Panel", {
            layout: "border",
            dock: "right",
            width: this.rightWidth,
            items: [
                me.inspectorPanel,
                me.basketPanel,
                me.miniMapPanel,
                me.legendPanel
            ]
        });

        me.mapPanel = Ext.create("NOC.inv.map.MapPanel", {
            app: me,
            readOnly: me.readOnly,
            listeners: {
                scope: me,
                mapready: me.onMapReady,
                changed: me.onChanged,
                openbasket: function() {
                    if(me.basketPanel.collapsed) {
                        me.basketButton.setPressed();
                    }
                },
                renderdone: function() {
                    me.miniMapPanel.scaleContentToFit();
                }
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
            glyph: NOC.glyph.sitemap,
            enableToggle: true,
            disabled: true,
            tooltip: __("Show STP topology"),
            scope: me,
            handler: me.onStp
        });

        me.viewAllNodeButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.eye,
            enableToggle: true,
            pressed: false,
            tooltip: __("Show all nodes"),
            scope: me,
            handler: me.onReload
        });

        me.legendButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.info,
            tooltip: __("Show/Hide legend"),
            enableToggle: true,
            listeners: {
                scope: me,
                toggle: me.onLegend
            }
        });

        me.miniMapButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.map,
            tooltip: __("Show/Hide miniMap"),
            enableToggle: true,
            pressed: true,
            listeners: {
                scope: me,
                toggle: me.onMiniMap
            }
        });

        me.basketButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.shopping_basket,
            tooltip: __("Show/Hide basket"),
            enableToggle: true,
            listeners: {
                scope: me,
                toggle: me.onBasket
            }
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
                        me.rotateButton,
                        "-",
                        me.addressIPButton,
                        me.viewMapButton,
                        me.viewLoadButton,
                        "-",
                        me.viewStpButton,
                        me.viewAllNodeButton,
                        "->",
                        me.basketButton,
                        me.miniMapButton,
                        me.legendButton
                    ]
                },
                me.rightPanel
            ],
            items: [me.mapPanel]
        });
        me.callParent();
    },

    loadSegment: function(segmentId) {
        var me = this;

        if(me.segmentCombo.getValue() == null) {
            me.segmentCombo.restoreById(segmentId);
        }
        me.setHistoryHash(segmentId);
        // @todo: Remove
        me.mapPanel.loadSegment(segmentId);
        me.currentSegmentId = segmentId;
        // @todo: Restrict to permissions
        me.editButton.setDisabled(me.readOnly);
        me.editButton.setPressed(false);
        me.saveButton.setDisabled(true);
        me.newLayoutButton.setDisabled(true);
        me.rotateButton.setDisabled(true);
        me.revertButton.setDisabled(true);
        me.inspectSegment();
        me.viewMapButton.setPressed(true);
        me.viewStpButton.setPressed(false);
        me.zoomCombo.setValue(1.0);
        me.mapPanel.setZoom(1.0);
    },

    onMapReady: function() {
        var me = this;

        if(me.getCmd() === "history") {
            me.loadSegment(me.noc.cmd.args[0]);
        }
        me.miniMapPanel.createMini(me.mapPanel);
    },

    onSelectSegment: function(combo, record, opts) {
        var me = this;
        if(record) {
            me.loadSegment(record.get("id"));
        }
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
            me.segmentInspector.preview(me.currentSegmentId, null);
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

    inspectCloud: function(linkId) {
        var me = this;
        me.inspectorPanel.getLayout().setActiveItem(
            me.cloudInspector
        );
        me.cloudInspector.preview(me.currentSegmentId, linkId);
    },

    onEdit: function() {
        var me = this;
        if(me.editButton.pressed) {
            me.mapPanel.setOverlayMode(0);
            me.viewMapButton.setPressed(true);
            me.rotateButton.setDisabled(false);
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
            me.newLayoutButton.setDisabled(me.readOnly);
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

    onRotate: function() {
        var me = this;
        me.mapPanel.onRotate();
    },

    onChangeName: function() {
      var me = this;
        me.mapPanel.changeLabelText(me.addressIPButton.pressed);
    },

    onStp: function() {
        var me = this;
        me.mapPanel.setStp(me.viewStpButton.pressed);
    },

    onLegend: function() {
        this.legendPanel.toggleCollapse();
    },

    onMiniMap: function() {
        this.miniMapPanel.toggleCollapse();
    },

    onBasket: function() {
        this.basketPanel.toggleCollapse();
    }
});
