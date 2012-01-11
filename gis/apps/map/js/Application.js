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
                    {
                        text: "Base Layer"
                    },
                    {
                        xtype: "textfield"
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
                            this.create_map(Ext.decode(response.responseText));
                        }
                    });
                }
            }
        });
        //
        this.callParent(arguments);
    },

    create_map: function(layers) {
        if(!layers.length) {
            Ext.Msg.alert("Error", "Incomplete GIS setup");
            return;
        }
        var map_div = "ol-map-" + this.id;
        // Create OpenLayers map
        this.ol_map = new OpenLayers.Map(map_div, {
            projection: "EPSG:900913",
            displayProjection: "EPSG:900913"
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
                        isBaseLayer: true
                    });
                    break;
                // TMS type
                case "TMS":
                    l = new OpenLayers.Layer.TMS(layer.name, layer.url,
                        {
                            layername: layer.layername,
                            type: "png",
                            sphericalMercator: true,
                            isBaseLayer: true
                        }
                    );
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
            new OpenLayers.Control.LayerSwitcher({}),
            new OpenLayers.Control.KeyboardDefaults(),
            new OpenLayers.Control.ScaleLine({
                geodesic: true
            }),
            // new OpenLayers.Control.MousePosition({}),
            new OpenLayers.Control.Graticule({visible: false})
        ]);
        //
        if(!this.ol_map.getCenter())
            this.ol_map.zoomToMaxExtent();
    }
});
