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
    //requires: [],

    initComponent: function() {
        // Create layer store
        this.layer_store = Ext.create("Ext.data.Store", {
            fields: ["layer"],
            data: []
        })
        // Create times
        Ext.apply(this, {
            dockedItems: [{
                xtype: "toolbar",
                dock: "top",
                items: [
                    {
                        text: "Area"
                    },
                    {
                        xtype: "textfield"
                    },
                    Ext.create("Ext.form.ComboBox", {
                        fieldLabel: "Base Layer",
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
        var urls = ["/static/js/ol/OpenLayers.js"];

        for(var i=0; i < layers.length; i++) {
            var layer = layers[i];
            switch(layer.type) {
                case "Google":
                    if(!init_GoogleAPI) {
                        init_GoogleAPI = true;
                        urls.push("http://maps.google.com/maps/api/js?sensor=false");
                    }
                    break;
            }
        }
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
        var map_div = "ol-map-" + this.id;
        // Create OpenLayers map
        this.ol_map = new OpenLayers.Map(map_div, {
            projection: "EPSG:900913",
            displayProjection: "EPSG:900913",
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
            // new OpenLayers.Control.MousePosition({}),
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
    }
});
