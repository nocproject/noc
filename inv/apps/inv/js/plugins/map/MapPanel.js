//---------------------------------------------------------------------
// inv.inv Map panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.map.MapPanel");

Ext.define("NOC.inv.inv.plugins.map.MapPanel", {
    extend: "Ext.panel.Panel",
    requires: [
    ],
    title: "Map",
    closable: false,
    layout: "fit",
    autoScroll: true,

    initComponent: function() {
        var me = this;
        //
        me.centerButton = Ext.create("Ext.button.Button", {
            tooltip: "Center to object",
            glyph: NOC.glyph.map_marker,
            scope: me,
            handler: me.centerToObject
        });

        me.zoomInButton = Ext.create("Ext.button.Button", {
            tooltip: "Zoom in",
            glyph: NOC.glyph.zoom_in,
            disabled: true,
            scope: me,
            handler: me.onZoomIn
        });

        me.zoomOutButton = Ext.create("Ext.button.Button", {
            tooltip: "Zoom out",
            glyph: NOC.glyph.zoom_out,
            disabled: true,
            scope: me,
            handler: me.onZoomOut
        });

        // Map panel
        Ext.apply(me, {
            dockedItems: [{
                xtype: "toolbar",
                dock: "top",
                items: [
                    me.centerButton,
                    me.zoomInButton,
                    me.zoomOutButton
                ]
            }],
            items: [
                {
                    xtype: "panel",
                    // Generate unique id
                    html: "<div id='ol-map-" + me.id + "' style='width: 100%; height: 100%;'></div>"
                }
            ]
        });
        me.callParent();
    },
    //
    //
    createMap: function(zoom, x, y, layers) {
        var me = this,
            mapDiv = "ol-map-" + me.id;

        me.objectX = x;
        me.objectY = y;
        me.objectZoom = zoom;

        me.projGeo = new OpenLayers.Projection("EPSG:4326");
        me.projMap = new OpenLayers.Projection("EPSG:900913");
        // Create OpenLayers map
        me.olMap = new OpenLayers.Map(mapDiv, {
            projection: me.projMap,
            displayProjection: me.projMap,
            controls: [
                new OpenLayers.Control.Navigation(),
                // new OpenLayers.Control.PanZoomBar(),
                new OpenLayers.Control.KeyboardDefaults(),
                new OpenLayers.Control.ScaleLine({geodesic: true}),
                new OpenLayers.Control.MousePosition({
                    displayProjection: me.projGeo
                }),
                new OpenLayers.Control.Graticule({visible: false})
            ]
        });
        // Create OSM layer
        me.olMap.addLayer(
            new OpenLayers.Layer.OSM("OSM")
        );
        // Center map
        me.centerToObject();
        // Create vector layers
        for(var i in layers) {
            var ld = layers[i],
                layer = new OpenLayers.Layer.Vector(ld.name, {
                    minZoomLevel: ld.min_zoom,
                    maxZoomLevel: ld.max_zoom,
                    protocol: new OpenLayers.Protocol.HTTP({
                        url: "/inv/inv/plugin/map/layers/" + ld.code + "/",
                        format: new OpenLayers.Format.GeoJSON({}),
                        srsInBBOX: true
                    }),
                    strategies: [new OpenLayers.Strategy.BBOX()],
                    styleMap: new OpenLayers.StyleMap({
                        default: {
                            pointRadius: 5,
                            strokeColor: ld.stroke_color,
                            fillColor: ld.fill_color,
                            label: "${label}",
                            labelAlign: "lb",
                            labelXOffset: 7,
                            labelOutlineColor: "white",
                            labelOutlineWidth: 3
                        }
                    })
                });
            me.olMap.addLayer(layer);
        }
    },
    //
    preview: function(data) {
        var me = this,
            urls = [];
        me.currentId = data.id;
        urls.push("/static/pkg/openlayers/OpenLayers.js");
        console.log(">>>", data);
        load_scripts(urls, me, function() {
            me.createMap(data.zoom, data.x, data.y, data.layers);
        });
    },
    //
    centerToObject: function() {
        var me = this;
        me.olMap.setCenter(
            new OpenLayers.LonLat(me.objectX, me.objectY).transform(
                me.projGeo, me.projMap),
            me.objectZoom
        );
        me.updateZoomButtons();
    },
    //
    onZoomIn: function() {
        var me = this;
        me.olMap.zoomIn();
        me.updateZoomButtons();
    },
    //
    onZoomOut: function() {
        var me = this;
        me.olMap.zoomOut();
        me.updateZoomButtons();
    },
    //
    updateZoomButtons: function() {
        var me = this,
            z = me.olMap.zoom;
        me.zoomInButton.setDisabled(z > 16);
        me.zoomOutButton.setDisabled(z <= 2);
    }
});
