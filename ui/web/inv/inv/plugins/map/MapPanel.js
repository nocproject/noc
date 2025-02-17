//---------------------------------------------------------------------
// inv.inv Leaflet Map panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.map.MapPanel");

Ext.define("NOC.inv.inv.plugins.map.MapPanel", {
  extend: "Ext.panel.Panel",
  requires: [
    "NOC.core.MapLayersCreator",
    "NOC.core.ResourceLoader",
  ],
  title: __("Map"),
  closable: false,
  layout: "fit",
  autoScroll: true,
  minZoomLevel: 0,
  maxZoomLevel: 19,
  mixins: [
    "NOC.inv.inv.plugins.Mixins",
  ],
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
    "1:1 000",
  ],

  initComponent: function(){
    var me = this;
    //
    me.infoTemplate = '<b>{0}</b><br><i>{1}</i><br><hr><a id="{2}" href="api/card/view/object/{3}/" target="_blank">Show...</a>';
    // Layers holder
    me.layers = [];
    // Object layer
    me.objectLayer = undefined;
    //
    me.centerButton = Ext.create("Ext.button.Button", {
      tooltip: __("Center to object"),
      glyph: NOC.glyph.location_arrow,
      scope: me,
      handler: me.centerToObject,
    });
    me.zoomLevelButton = Ext.create("Ext.button.Button", {
      tooltip: __("Zoom to level"),
      text: __("1:100 000"),
      menu: {
        items: me.zoomLevels.map(function(z, index){
          return {
            text: z,
            zoomLevel: index,
            scope: me,
            handler: me.onZoomLevel,
          }
        }),
      },
    });
    //
    me.setPositionButton = Ext.create("Ext.button.Button", {
      tooltip: __("Set position"),
      glyph: NOC.glyph.map_marker,
      enableToggle: true,
      listeners: {
        scope: me,
        toggle: me.onSetPositionToggle,
      },
    });
    me.mapPanel = Ext.create("Ext.panel.Panel", {
      xtype: "panel",
      // Generate unique id
      html: "<div id='leaf-map-" + me.id + "' style='width: 100%; height: 100%;'></div>",
    });
    // Map panel
    Ext.apply(me, {
      dockedItems: [{
        xtype: "toolbar",
        dock: "top",
        items: [
          me.centerButton,
          me.zoomLevelButton,
          "-",
          me.setPositionButton,
        ],
      }],
      items: [me.mapPanel],
    });
    me.callParent();
  },
  //
  preview: function(data){
    var me = this;

    this.currentId = data.id;
    NOC.core.ResourceLoader.loadSet("leaflet", {
      yandex: NOC.settings.gis.yandex_supported,
    })
    .then(() => {
      me.createMap(data);
    })
    .catch(() => {
      NOC.error(__("Failed to load map resources"));
    });
  },
  //
  createLayer: function(cfg, objectLayer){
    var me = this,
      layer;
    layer = L.geoJSON({
      "type": "FeatureCollection",
      "features": [],
    }, {
      nocCode: cfg.code,
      nocMinZoom: cfg.min_zoom,
      nocMaxZoom: cfg.max_zoom,
      pointToLayer: function(geoJsonPoint, latlng){
        return L.circleMarker(latlng, {
          color: cfg.fill_color,
          fillColor: cfg.fill_color,
          fillOpacity: 1,
          radius: 5,
        });
      },
      style: function(){
        return {
          color: cfg.fill_color,
          fillColor: cfg.fill_color,
          strokeColor: cfg.stroke_color,
          weight: cfg.stroke_width,
        };
      },
      filter: function(){
        // Remove invisible layers on zoom
        var zoom = me.map.getZoom();
        return (zoom >= cfg.min_zoom) && (zoom <= cfg.max_zoom)
      },
    });
    if(cfg.code === objectLayer){
      me.objectLayer = layer;
    }
    layer.on("click", Ext.bind(me.showObjectTip, me));
    layer.on("add", Ext.bind(me.visibilityHandler, me));
    layer.on("remove", Ext.bind(me.visibilityHandler, me));
    if(cfg.is_visible){
      layer.addTo(me.map);
    }
    me.layersControl.addOverlay(layer, cfg.name);
    return layer;
  },
  //
  loadLayer: function(layer){
    var me = this,
      zoom = me.map.getZoom();
    if((zoom < layer.options.nocMinZoom) || (zoom > layer.options.nocMaxZoom)){
      // Not visible
      layer.clearLayers();
      return;
    }
    if(me.map.hasLayer(layer)){
      Ext.Ajax.request({
        url: "/inv/inv/plugin/map/layers/" + me.getQuery(layer.options.nocCode),
        method: "GET",
        scope: me,
        success: function(response){
          var data = Ext.decode(response.responseText);
          layer.clearLayers();
          if(!Ext.Object.isEmpty(data)){
            layer.addData(data);
          }
        },
        failure: function(){
          NOC.error(__("Failed to get layer"));
        },
      });
    }
  },
  //
  getQuery: function(layerCode){
    return Ext.String.format(layerCode + "/?bbox={0},EPSG%3A4326", this.map.getBounds().toBBoxString());
  },
  //
  onRefresh: function(){
    var me = this;
    Ext.each(me.layers, function(layer){
      me.loadLayer(layer);
    });
  },
  //
  createMap: function(data){
    var me = this,
      mapDiv = "leaf-map-" + me.id,
      mapLayersCreator = Ext.create("NOC.core.MapLayersCreator", {
        default_layer: NOC.settings.gis.default_layer, 
        allowed_layers: NOC.settings.gis.base,
        yandex_supported: NOC.settings.gis.yandex_supported,
        translator: __,
      }),
      mapDom = Ext.select("#" + mapDiv).elements[0];
    me.center = [data.y, data.x];
    me.contextMenuData = data.add_menu;
    me.initScale = data.zoom;
    //
    if(me.map){
      me.map.remove();
    }
    me.map = L.map(mapDom, {
      zoomControl: false,
      attributionControl: false,
    }).setView(me.center, me.initScale);

    me.map.on("contextmenu", Ext.bind(me.onContextMenu, me));
    me.map.on("moveend", Ext.bind(me.onRefresh, me));
    me.map.on("zoomend", Ext.bind(me.onZoomEnd, me));
    me.map.on("click", Ext.bind(me.onSetPositionClick, me));
    //
    L.control.zoom({
      zoomInTitle: __("Zoom in..."),
      zoomOutTitle: __("Zoom out..."),
    }).addTo(me.map);
    //

    mapLayersCreator.run(me);

    me.layers = [];
    Ext.each(data.layers, function(cfg){
      me.layers.push(me.createLayer(cfg, data.layer));
    });
    me.onRefresh();
  },
  //
  visibilityHandler: function(e){
    var me = this, status = e.type === "add";
    Ext.Ajax.request({
      url: "/inv/inv/plugin/map/layer_visibility/",
      method: "POST",
      jsonData: {
        layer: e.target.options.nocCode,
        status: status,
      },
      scope: me,
      success: function(){
        var me = this;
        if(status){
          me.loadLayer(e.target);
        }
      },
      failure: function(){
        NOC.error(__("Failed to change layer settings"));
      },
    });

  },
  //
  centerToObject: function(){
    var me = this;
    me.map.setView(me.center, me.initScale);
    me.updateZoomButtons();
  },
  //
  showObjectTip: function(args){
    var resource = args.layer.feature.properties.resource,
      app = this.up("[appId=inv.inv]"),
      position = [args.originalEvent.clientX, args.originalEvent.clientY];
    this.showBalloon(app, "mapBalloon", resource, position);
  },
  //
  onContextMenu: function(event){
    var me = this,
      m = me.getContextMenu();
    me.event = event;
    m.showAt(event.originalEvent.clientX, event.originalEvent.clientY);
  },
  //
  getContextMenu: function(){
    var me = this,
      addHandler = function(items){
        Ext.each(items, function(item){
          if(Object.prototype.hasOwnProperty.call(item, "menu")){
            addHandler(item.menu);
          } else if(Object.prototype.hasOwnProperty.call(item, "objectTypeId")){
            item.listeners = {
              scope: me,
              click: me.onContextMenuAdd,
            }
          }
        });
        return items;
      };
    // Return cached
    if(me.contextMenu){
      return me.contextMenu;
    }
    me.contextMenu = Ext.create("Ext.menu.Menu", {
      renderTo: me.mapDom,
      items: [
        {
          text: __("Add"),
          menu: addHandler(me.contextMenuData),
        },
      ],
    });
    return me.contextMenu;
  },
  //
  onContextMenuAdd: function(item){
    var me = this;
    Ext.create("NOC.inv.inv.plugins.map.AddObjectForm", {
      app: me,
      objectModelId: item.objectTypeId,
      objectModelName: item.text,
      newPosition: {
        lon: me.event.latlng.lng,
        lat: me.event.latlng.lat,
      },
      positionSRID: "EPSG:4326",
    }).show();
  },
  //
  onZoomLevel: function(item){
    var me = this;
    me.map.setZoom(item.zoomLevel);
    me.updateZoomButtons();
  },
  //
  updateZoomButtons: function(){
    var me = this;
    me.zoomLevelButton.setText(me.zoomLevels[me.map.getZoom()]);
  },
  //
  onZoomEnd: function(){
    var me = this;
    me.updateZoomButtons();
  },
  //
  onSetPositionClick: function(e){
    var me = this;
    if(me.setPositionButton.pressed){
      me.setPositionButton.toggle(false);
      Ext.Ajax.request({
        url: "/inv/inv/" + me.currentId + "/plugin/map/set_geopoint/",
        method: "POST",
        jsonData: {
          srid: "EPSG:4326",
          x: e.latlng.lng,
          y: e.latlng.lat,
        },
        scope: me,
        success: function(){
          var data = {
              crs: "EPSG:4326",
              type: "FeatureCollection",
              features: [
                {
                  geometry: {
                    type: "Point",
                    coordinates: [e.latlng.lng, e.latlng.lat],
                  },
                  type: "Feature",
                  id: me.currentId,
                  properties: {
                    object: me.currentId,
                    label: "",
                  },
                }],
            },
            layers = me.objectLayer.getLayers().filter(function(layer){
              return layer.feature.id !== me.currentId
            });
          me.objectLayer.clearLayers();
          layers.map(function(layer){
            layer.addTo(me.objectLayer);
          });
          me.objectLayer.addData(data);
          if(!me.map.hasLayer(me.objectLayer)){
            me.objectLayer.addTo(me.map);
          }
        },
        failure: function(){
          NOC.error(__("Failed to set position"));
        },
      });
    }
  },
  //
  onSetPositionToggle: function(self){
    this.mapPanel.getEl().dom.querySelector(".leaflet-container").style.cursor = self.pressed ? "crosshair" : "";
  },
});
