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
    minZoomLevel: 0,
    maxZoomLevel: 19,
    // Zoom levels according to
    // http://wiki.openstreetmap.org/wiki/Zoom_levels
    zoomLevels: [
        "1:500 000 000",
        "1:250 000 000 (Whole world)",
        "1:150 000 000",
        "1:70 000 000",
        "1:35 000 000",
        "1:15 000 000",
        "1:10 000 000",
        "1:4 000 000 (Region)",
        "1:2 000 000",
        "1:1 000 000",
        "1:500 000",
        "1:250 000 (Large city)",
        "1:150 000",
        "1:70 000",
        "1:35 000",
        "1:15 000 (Block)",
        "1:8 000",
        "1:4 000 (Building)",
        "1:2 000",
        "1:1 000"
    ],

    initComponent: function() {
        var me = this;
        // Base Layers
        me.requireGoogleAPI = false;
        me.baseLayers = [];

        if(NOC.settings.gis.base.enable_osm) {
            // OpenStreetMap layer
            me.baseLayers.push({
                text: "OpenStreetMap",
                layerType: "osm",
                scope: me,
                handler: me.onSelectBaseLayer
            });
        }
        if(NOC.settings.gis.base.enable_google_sat) {
            // Google sattelite layer
            me.baseLayers.push({
                text: "Google Sattelite",
                layerType: "google_sat",
                scope: me,
                handler: me.onSelectBaseLayer
            });
            me.requireGoogleAPI = true;
        }
        if(NOC.settings.gis.base.enable_google_roadmap) {
            // Google roadmap layer
            me.baseLayers.push({
                text: "Google Roadmap",
                layerType: "google_roadmap",
                scope: me,
                handler: me.onSelectBaseLayer
            });
            me.requireGoogleAPI = true;
        }
        //
        me.centerButton = Ext.create("Ext.button.Button", {
            tooltip: "Center to object",
            glyph: NOC.glyph.location_arrow,
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

        me.zoomLevelButton = Ext.create("Ext.button.Button", {
            tooltip: "Zoom to level",
            text: "1:100 000",
            menu: {
                items: me.zoomLevels.map(function(z, index) {
                    return {
                        text: z,
                        zoomLevel: index,
                        scope: me,
                        handler: me.onZoomLevel
                    }
                })
            }
        });

        me.setPositionButton = Ext.create("Ext.button.Button", {
            tooltip: "Set position",
            glyph: NOC.glyph.map_marker,
            enableToggle: true,
            listeners: {
                scope: me,
                toggle: me.onSetPositionToggle
            }
        });

        me.layersButton = Ext.create("Ext.button.Button", {
            tooltip: "Setup layers",
            text: "Layers",
            glyph: NOC.glyph.align_justify,
            menu: {
                items: []
            }
        });

        me.baseLayerButton = Ext.create("Ext.button.Button", {
            tooltip: "Select base layer",
            text: me.baseLayers[0].text,
            menu: {
                items: me.baseLayers
            }
        });

        // Map panel
        Ext.apply(me, {
            dockedItems: [{
                xtype: "toolbar",
                dock: "top",
                items: [
                    me.centerButton,
                    me.zoomInButton,
                    me.zoomOutButton,
                    me.zoomLevelButton,
                    "-",
                    me.setPositionButton,
                    "->",
                    me.layersButton,
                    me.baseLayerButton
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
        //
        me.infoTemplate = Handlebars.compile(
            "<b>{{name}}</b><br>" +
            "<i>{{model}}</i><br><hr>" +
            "<a id='{{showLinkId}}' href='#'>Show...</a>"
        );
    },
    //
    //
    createMap: function(zoom, x, y, objectLayer, layers) {
        var me = this,
            mapDiv = "ol-map-" + me.id;

        me.objectX = x;
        me.objectY = y;
        me.objectZoom = zoom;

        me.projGeo = new OpenLayers.Projection("EPSG:4326");
        me.projMap = new OpenLayers.Projection("EPSG:900913");
        //
        me.graticuleControl = new OpenLayers.Control.Graticule({
            visible: false
        });
        //
        me.setPositionControl = new OpenLayers.Control.Click({
            scope: me,
            fn: me.onSetPositionClick
        });
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
                me.graticuleControl,
                me.setPositionControl
            ]
        });
        // Create base layers
        Ext.each(me.baseLayers, function(v) {
            switch(v.layerType) {
                case "osm":
                    me.olMap.addLayer(new OpenLayers.Layer.OSM(v.text));
                    break;
                case "google_sat":
                    me.olMap.addLayer(
                        new OpenLayers.Layer.Google(v.text, {
                            type: "satellite"
                        })
                    );
                    break;
                case "google_roadmap":
                    me.olMap.addLayer(
                        new OpenLayers.Layer.Google(v.text, {
                            type: "roadmap"
                        })
                    );
                    break;
                default:
                    console.log("Invalid base layer " + v.layerType);
            }
        });
        // Create OSM layer
        me.olMap.addLayer(
            new OpenLayers.Layer.OSM("OSM")
        );
        // Center map
        me.centerToObject();
        // Create vector layers
        me.objectLayer = null;
        zoom = me.olMap.getZoom();
        me.layerZoom = []; // {<layer>, <min zoom>, <max zoom>, isVisible}
        for(var i in layers) {
            var ld = layers[i],
                layer = new OpenLayers.Layer.Vector(ld.name, {
                    protocol: new OpenLayers.Protocol.HTTP({
                        url: "/inv/inv/plugin/map/layers/" + ld.code + "/",
                        format: new OpenLayers.Format.GeoJSON({}),
                        srsInBBOX: true
                    }),
                    strategies: [new OpenLayers.Strategy.BBOX()],
                    visibility: ld.is_visible && (zoom >= ld.min_zoom) && (zoom <= ld.max_zoom),
                    styleMap: new OpenLayers.StyleMap({
                        default: {
                            pointRadius: ld.point_radius,
                            strokeWidth: ld.stroke_width,
                            strokeColor: ld.stroke_color,
                            fillColor: ld.fill_color,
                            label: ld.show_labels ? "${label}" : "",
                            labelAlign: "lb",
                            labelXOffset: 7,
                            labelOutlineColor: "white",
                            labelOutlineWidth: 3,
                            strokeDashstyle: ld.strokeDashstyle,
                            graphicName: ld.point_graphic
                        },
                        select: {
                            labelAlign: "lb",
                            labelOutlineColor: "#FFFFCC",
                            strokeColor: "yellow"
                        }
                    })
                });
            me.olMap.addLayer(layer);
            if(ld.code == objectLayer) {
                me.objectLayer = layer;
            }
            // Set up zoom levels
            me.layerZoom.push({
                layer: layer,
                code: ld.code,
                minZoom: ld.min_zoom,
                maxZoom: ld.max_zoom,
                isVisible: ld.is_visible
            });
            // Add to layers menu
            me.layersButton.menu.add({
                text: ld.name,
                checked: ld.is_visible,
                scope: me,
                checkHandler: me.onChangeLayerVisibility,
                layerCode: ld.code
            });
        }
        //
        me.olMap.events.on({
            zoomend: Ext.bind(me.setLayerVisibility, me),
            featureclick: Ext.bind(me.onFeatureClick, me),
            featureover: Ext.bind(me.onFeatureOver, me),
            featureout: Ext.bind(me.onFeatureOut, me)
        });
        me.setLayerVisibility();
        me.infoPopup = null;
        // Install context menu
        me.mapDom = Ext.select("#" + mapDiv).elements[0];
        me.mapDom.oncontextmenu = Ext.bind(me.onContextMenu, me);
    },
    //
    preview: function(data) {
        var me = this,
            urls = [];
        me.currentId = data.id;
        me.contextMenuData = data.add_menu;
        urls.push("/static/pkg/openlayers/OpenLayers.js");
        if(me.requireGoogleAPI) {
            urls.push("@http://maps.google.com/maps/api/js?sensor=false&callback=_noc_load_callback");
        }
        urls.push("/static/js/noc/OpenLayers.js");
        load_scripts(urls, me, function() {
            me.createMap(data.zoom, data.x, data.y, data.layer, data.layers);
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
        me.zoomInButton.setDisabled(z >= me.maxZoomLevel);
        me.zoomOutButton.setDisabled(z <= me.minZoomLevel);
        me.zoomLevelButton.setText(me.zoomLevels[z]);
    },
    //
    onZoomLevel: function(item, e) {
        var me = this;
        me.olMap.zoomTo(item.zoomLevel);
        me.updateZoomButtons();
    },
    //
    onSelectBaseLayer: function(item, e) {
        var me = this;
        me.baseLayerButton.setText(item.text);
        me.olMap.setBaseLayer(me.olMap.getLayersByName(item.text)[0]);
    },
    //
    onSetPositionClick: function(e) {
        var me = this,
            mc = me.olMap.getLonLatFromPixel(e.xy);
        me.setPositionButton.toggle(false);
        mc.transform(me.projMap, me.projGeo);
        Ext.Ajax.request({
            url: "/inv/inv/" + me.currentId + "/plugin/map/set_geopoint/",
            method: "POST",
            jsonData: {
                srid: me.projGeo.projCode,
                x: mc.lon,
                y: mc.lat
            },
            scope: me,
            success: function() {
                me.objectLayer.loaded = false;
                me.objectLayer.setVisibility(true);
                me.objectLayer.refresh({force: true});
            },
            failure: function(response) {
                NOC.error("Failed to set position");
            }
        });
    },
    //
    onSetPositionToggle: function(button, pressed, eOpts) {
        var me = this;
        if(pressed) {
            me.setPositionControl.activate();
        } else {
            me.setPositionControl.deactivate();
        }
    },
    // Adjust vector layers visibility
    setLayerVisibility: function() {
        var me = this,
            zoom = me.olMap.getZoom();
        Ext.each(me.layerZoom, function(l) {
            l.layer.setVisibility(l.isVisible && (zoom >= l.minZoom) && (zoom <= l.maxZoom));
        });
    },
    //
    showObjectPopup: function(feature, data) {
        var me = this,
            showLinkId = "noc-ol-tip-show-link-" + me.id,
            text, ttEl, showLink;
        data = Ext.merge({showLinkId: showLinkId}, data);
        text = me.infoTemplate(data);
        if(me.infoPopup) {
            me.olMap.removePopup(me.infoPopup);
            me.infoPopup.destroy();
            me.infoPopup = null;
        }
        me.infoPopup = new OpenLayers.Popup.FramedCloud(
            "popup",
            OpenLayers.LonLat.fromString(feature.geometry.toShortString()),
            null,
            text,
            null,
            true
        );
        me.olMap.addPopup(me.infoPopup);
        ttEl = Ext.get(me.infoPopup.contentDiv);
        showLink = ttEl.select("#" + showLinkId).elements[0];
        showLink.onclick = function() {
            me.app.showObject(data.id);
        }
    },
    //
    onFeatureClick: function(e) {
        var me = this;
        if(!e.feature.attributes.object) {
            return;
        }
        Ext.Ajax.request({
            url: "/inv/inv/" + e.feature.attributes.object + "/plugin/map/object_data/",
            method: "GET",
            scope: me,
            success: function(response) {
                me.showObjectPopup(e.feature, Ext.decode(response.responseText));
            },
            failure: function() {
                NOC.error("Failed to get data");
            }
        });
    },
    //
    onFeatureOver: function(e) {
        var me = this,
            text = "text";
        e.feature.renderIntent = "select";
        e.feature.layer.drawFeature(e.feature);
    },
    //
    onFeatureOut: function(e) {
        var me = this;
        e.feature.renderIntent = "default";
        e.feature.layer.drawFeature(e.feature);
    },
    //
    onChangeLayerVisibility: function(item, checked) {
        var me = this;
        Ext.Ajax.request({
            url: "/inv/inv/plugin/map/layer_visibility/",
            method: "POST",
            jsonData: {
                layer: item.layerCode,
                status: checked
            },
            scope: me,
            success: function() {
                Ext.each(me.layerZoom, function(v) {
                    if(v.code == item.layerCode) {
                        v.isVisible = checked;
                        me.setLayerVisibility();
                    }
                });
            },
            failure: function() {
                NOC.error("Failed to change layer settings");
            }
        });
    },
    //
    getContextMenuAddItems: function(items) {
        var me = this;
        Ext.each(items, function(i) {
            if(i.menu) {
                i.menu = me.getContextMenuAddItems(i.menu);
            } else if(i.objectTypeId) {
                i.listeners = {
                    scope: me,
                    click: me.onContextMenuAdd
                }
            }
        });
        return items;
    },
    //
    getContextMenu: function() {
        var me = this;
        // Return cached
        if(me.contextMenu) {
            return me.contextMenu;
        }
        // create new
        // @todo: Install handlers?
        me.contextMenu = Ext.create("Ext.menu.Menu", {
            renderTo: me.mapDom,
            items: [
                {
                    text: "Add",
                    menu: me.getContextMenuAddItems(me.contextMenuData)
                }
            ]
        });
        return me.contextMenu;
    },
    //
    onContextMenu: function(e) {
        var me = this,
            m = me.getContextMenu();
        //
        e = e ? e : window.event;
        // Calculate map position
        console.log(e.layerX, e.layerY);
        me.newPosition = me.olMap.getLonLatFromPixel(new OpenLayers.Pixel(e.layerX, e.layerY));
        me.newPosition.transform(me.projMap, me.projGeo);
        // Show context menu
        m.setLocalXY(e.layerX, e.layerY);
        m.show();
        // Disable default context menu
        if(e.preventDefault) {
            e.preventDefault(); // normal browsers
        } else {
            return false; // MSIE
        }
    },
    //
    onContextMenuAdd: function(item, e, eOpts) {
        var me = this;
        Ext.create("NOC.inv.inv.plugins.map.AddObjectForm", {
            app: me,
            objectModelId: item.objectTypeId,
            objectModelName: item.text,
            newPosition: me.newPosition,
            positionSRID: me.projGeo.projCode
        }).show();
    }
});
