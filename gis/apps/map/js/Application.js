//---------------------------------------------------------------------
// gis.map application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.gis.map.Application");

Ext.define("NOC.gis.map.Application", {
    extend: "NOC.core.Application",
    layout: "fit",
    requires: [
        "NOC.gis.area.LookupField",
        "NOC.gis.overlay.LookupField"
    ],

    initComponent: function() {
        // Create layer store
        this.layer_store = Ext.create("Ext.data.Store", {
            fields: ["layer"],
            data: []
        });
        this.overlays = {};  // id -> OpenLayers.Layer.Vector instance
        // Create times
        Ext.apply(this, {
            dockedItems: [{
                xtype: "toolbar",
                dock: "top",
                items: [
                    {
                        xtype: "gis.area.LookupField",
                        fieldLabel: "Area",
                        labelWidth: 30,
                        name: "area",
                        allowBlank: true,
                        listeners: {
                            select: function(combo, records, opts) {
                                var area_id = records[0].data.id;
                                this.up().up().zoom_to_area(area_id);
                            }
                        }
                    },
                    Ext.create("Ext.form.ComboBox", {
                        fieldLabel: "Base Layer",
                        labelWidth: 65,
                        store: this.layer_store,
                        queryMode: "local",
                        displayField: "layer",
                        valueField: "layer",
                        itemId: "layer-combo",
                        listeners: {
                            select: function(combo, records, opts) {
                                var m = this.up().up().ol_map;
                                var l = m.getLayersByName(records[0].data.layer)[0];
                                m.setBaseLayer(l);
                            }
                        }
                    }),
                    {
                        xtype: "gis.overlay.LookupField",
                        fieldLabel: "Overlays",
                        labelWidth: 50,
                        name: "overlays",
                        allowBlank: true,
                        multiSelect: true,
                        listeners: {
                            change: function(combo, new_value, old_value, opts) {
                                console.log(new_value, old_value);
                                var a = this.up().up();
                                // Disable deselected overlays
                                var i;
                                if(old_value) {
                                    for(i = 0; i < old_value.length; i++) {
                                        var overlay_id = old_value[i];
                                        if(new_value.indexOf(overlay_id) < 0)
                                            a.deactivate_overlay(overlay_id);
                                    }
                                }
                                // Enable selected overlays
                                for(i = 0; i < new_value.length; i++) {
                                    var overlay_id = new_value[i];
                                    if((old_value == undefined)
                                        || (old_value.indexOf(overlay_id) < 0))
                                        a.activate_overlay(overlay_id);
                                }
                            }
                        }
                    },
                    "->",
                    {
                        xtype: "checkboxfield",
                        boxLabel: "Show Grid",
                        listeners: {
                            change: function(cb, new_value, old_value, o) {
                                var m = this.up().up().ol_map;
                                if (m) {
                                    var l = m.getLayersByName("Graticule")[0];
                                    l.setVisibility(new_value);
                                }
                            }
                        }
                    }
                ]
            }],

            items: [
                {
                    xtype: "panel",
                    // Generate unique id
                    html: "<div id='ol-map-" + this.id + "' style='width: 100%; height: 100%;'></div>"
                }
            ],

            listeners: {
                afterrender: function() {
                    // Request layers
                    Ext.Ajax.request({
                        method: "GET",
                        url: "/gis/map/layers/",
                        scope: this,
                        success: function(response) {
                            this.init_map(Ext.decode(response.responseText));
                        }
                    });
                }
            }
        });
        //
        this.callParent(arguments);
    },

    //
    // Initialize all required javascript libraries
    //
    init_map: function(layers) {
        var init_GoogleAPI = false;
        var urls = [];

        for(var i=0; i < layers.length; i++) {
            var layer = layers[i];
            switch(layer.type) {
                case "Google":
                    if(!init_GoogleAPI) {
                        init_GoogleAPI = true;
                        urls.push("@http://maps.google.com/maps/api/js?sensor=false&callback=_noc_load_callback");
                    }
                    break;
            }
        }
        urls.push("/static/pkg/openlayers/OpenLayers.js");
        load_scripts(urls, this, function() {this.create_map(layers);});
    },
    //
    // Create and populate OpenLayers map
    //
    create_map: function(layers) {
        if(!layers.length) {
            Ext.Msg.alert("Error", "Incomplete GIS setup");
            return;
        }
        this.proj_geo = new OpenLayers.Projection("EPSG:4326");
        this.proj_mercator = new OpenLayers.Projection("EPSG:900913");
        var map_div = "ol-map-" + this.id;
        // Create OpenLayers map
        this.ol_map = new OpenLayers.Map(map_div, {
            projection: this.proj_mercator,
            displayProjection: this.proj_mercator,
            controls: []
        });
        //
        for(var i=0; i < layers.length; i++) {
            var layer = layers[i];
            var l = null;
            switch(layer.type) {
                // XYZ type
                case "XYZ":
                    l = new OpenLayers.Layer.XYZ(layer.name, layer.url, {
                        sphericalMercator: true,
                        isBaseLayer: layer.base
                    });
                    break;
                // TMS type
                case "TMS":
                    l = new OpenLayers.Layer.TMS(layer.name, "/gis/tms/", {
                        layername: layer.layername,
                        type: "png",
                        sphericalMercator: true,
                        isBaseLayer: layer.base
                    });
                    break;
                // OpenStreetMap
                case "OSM":
                    l = new OpenLayers.Layer.OSM(layer.name);
                    break;
                // Google Maps
                case "Google":
                    l = new OpenLayers.Layer.Google(layer.name, {
                        type: layer.google_type
                    });
                    break;
                // Error
                default:
                    console.log("Unknown layer type " + layer.type);
            }
            if(l)
                this.ol_map.addLayer(l);
        };
        // Controls
        this.ol_map.addControls([
            new OpenLayers.Control.Navigation(),
            new OpenLayers.Control.PanZoomBar(),
            new OpenLayers.Control.KeyboardDefaults(),
            new OpenLayers.Control.ScaleLine({geodesic: true}),
            new OpenLayers.Control.MousePosition({
                displayProjection: this.proj_geo
            }),
            new OpenLayers.Control.Graticule({visible: false})
        ]);
        // Center map
        if(!this.ol_map.getCenter())
            this.ol_map.zoomToMaxExtent();
        // Select layer in combobox
        var ld = [];
        for(var i=0; i < layers.length; i++) {
            var layer = layers[i];
            if(layer.base)
                ld.push({layer: layer.name});
        }
        this.layer_store.loadData(ld);
        // Switch layer combo to active layer
        var layer_combo = this.dockedItems.items[0].getComponent("layer-combo");
        layer_combo.select(this.ol_map.baseLayer.name);
    },
    //
    // Zoom and center to area
    //
    zoom_to_area: function(area_id) {
        Ext.Ajax.request({
            method: "GET",
            url: "/gis/area/" + area_id + "/",
            scope: this,
            success: function(response) {
                var area = Ext.decode(response.responseText);
                if(area.name == "World") {
                    this.ol_map.zoomToMaxExtent();
                    return;
                }
                var bounds = new OpenLayers.Bounds();
                bounds.extend(new OpenLayers.LonLat(area.SW[0], area.SW[1]));
                bounds.extend(new OpenLayers.LonLat(area.NE[0], area.NE[1]));
                bounds.transform(this.proj_geo, this.ol_map.getProjectionObject());
                console.log(bounds);
                this.ol_map.zoomToExtent(bounds, true);
            }
        });
    },
    //
    // Activate overlay
    //
    activate_overlay: function(overlay_id) {
        var layer = this.overlays[overlay_id];
        if(layer) {
            layer.setVisibility(true);
        } else {
            // Get overlay info
            Ext.Ajax.request({
                method: "GET",
                url: "/gis/overlay/" + overlay_id + "/",
                scope: this,
                success: function(response) {
                    // Create overlay
                    var info = Ext.decode(response.responseText);
                    var layer = new OpenLayers.Layer.Vector(info.name, {
                            protocol: new OpenLayers.Protocol.HTTP({
                                url: "/gis/overlay/gate/" + info.gate_id + "/",
                                format: new OpenLayers.Format.GeoJSON({
                                    externalProjection: this.proj_geo,
                                    internalProjection: this.proj_mercator
                                })
                            }),
                            strategies: [new OpenLayers.Strategy.BBOX()]
                        });
                        this.overlays[overlay_id] = layer;
                        this.ol_map.addLayer(layer);
                }
            });
        }
    },
    //
    // Deactivate overlay
    //
    deactivate_overlay: function(overlay_id) {
        this.overlays[overlay_id].setVisibility(false);
    }
});
