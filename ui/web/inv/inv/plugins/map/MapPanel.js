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
    "NOC.core.mixins.Ballon",
    "NOC.inv.inv.plugins.Mixins",
  ],
  pollingTaskId: undefined,
  pollingInterval: 10000,
  // ViewModel for this panel
  viewModel: {
    data: {
      autoReload: false,
      autoReloadIcon: "xf05e", // NOC.glyph.ban
      autoReloadText: __("Auto reload : OFF"),
      icon: "<i class='fa fa-fw' style='width:16px;'></i>",
    },
  },
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
  //
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
    //
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
          {
            text: __("Reload"),
            iconAlign: "right",
            enableToggle: true,
            bind: {
              glyph: "{autoReloadIcon}",
              tooltip: "{autoReloadText}",
              pressed: "{autoReload}",
            },
            listeners: {
              scope: me,
              toggle: me.onAutoReloadToggle,
            },
          },
          "->",
          {
            xtype: "tbtext",
            padding: "3 0 0 4",
            bind: {
              html: "{icon}",
            },
          },
        ],
      }],
      items: [me.mapPanel],
    });
    me.callParent();
    this.subscribeToEvents();
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
      layer = L.geoJSON({
        "type": "FeatureCollection",
        "features": [],
      }, {
        nocCode: cfg.code,
        nocMinZoom: cfg.min_zoom,
        nocMaxZoom: cfg.max_zoom,
        pointToLayer: function(geoJsonPoint, latlng){
          switch(cfg.point_graphic){
            case "circle": {
              let iconSize = cfg.point_radius * 4,
                anchorPoint = iconSize / 2;
              return L.marker(latlng, {
                icon: L.divIcon({
                  html: `<i class="fa fa-circle" style="color: ${cfg.fill_color}; font-size: ${iconSize}px;"></i>`,
                  iconSize: [0, 0],
                  iconAnchor: [anchorPoint, anchorPoint],
                  fontSize: iconSize,
                }),
              });
            }
            default:
              return L.circleMarker(latlng, {
                color: cfg.fill_color,
                fillColor: cfg.fill_color,
                fillOpacity: 1,
                radius: cfg.point_radius,
              });
          }
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
    me.updateStatuses();
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
  updateStatuses: function(){
    let resources = this.getVisibleResources();
    this.getViewModel().set("icon", this.generateIcon(true, "spinner", "grey", __("loading")));
    Ext.Ajax.request({
      url: "/inv/inv/plugin/map/resource_status/",
      method: "POST",
      jsonData: {
        resources: Object.keys(resources),
      },
      success: function(response){
        let data = Ext.decode(response.responseText);
        data.resource_status.forEach(item => {
          let resourceData = resources[item.resource];
          if(Ext.isDefined(resourceData.leafletLayer)){
            resourceData.leafletLayer.setIcon(
              this.createStatusIcon("alarm", resourceData.leafletLayer),
            );
          }
        });
      },
      failure: function(){
        NOC.error(__("Failed to update statuses"));
      },
      callback: function(){
        this.getViewModel().set("icon", this.generateIcon(true, "circle", NOC.colors.yes, __("online")));
      },
      scope: this,
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
  //
  onAutoReloadToggle: function(self){
    this.autoReloadIcon(self.pressed);
    this.autoReloadText(self.pressed);
    if(this.getViewModel()){
      this.getViewModel().set("icon", this.generateIcon(self.pressed, "circle", NOC.colors.yes, __("online")));
    }
    if(self.pressed){
      this.startPolling();
    } else{
      this.stopPolling();
    }
  },
  //
  autoReloadIcon: function(isReloading){
    //  NOC.glyph.refresh or NOC.glyph.ban
    this.getViewModel().set("autoReloadIcon", isReloading ? "xf021" : "xf05e");
  },
  //
  autoReloadText: function(isReloading){
    this.getViewModel().set("autoReloadText", __("Auto reload : ") + (isReloading ? __("ON") : __("OFF")));
  },
  //
  generateIcon: function(isUpdatable, icon, color, msg){
    if(isUpdatable){
      return `<i class='fa fa-${icon}' style='color:${color};width:16px;' data-qtip='${msg}'></i>`;
    }
    return "<i class='fa fa-fw' style='width:16px;'></i>";
  },
  //
  startPolling: function(){
    this.observer = new IntersectionObserver(function(entries){
      this.isIntersecting = entries[0].isIntersecting;
      this.disableHandler(!entries[0].isIntersecting);
    }.bind(this), {
      threshold: 0.1,
    });
    this.observer.observe(this.getEl().dom);
    if(Ext.isEmpty(this.pollingTaskId)){
      this.pollingTaskId = Ext.TaskManager.start({
        run: this.pollingTask,
        interval: this.pollingInterval,
        scope: this,
      });
    } else{
      this.pollingTask();
    }
  },
  //
  stopPolling: function(){
    if(this.pollingTaskId){
      Ext.TaskManager.stop(this.pollingTaskId);
      this.pollingTaskId = undefined;
    }
    if(!Ext.isEmpty(this.observer)){
      this.observer.unobserve(this.getEl().dom);
    }
  },
  //
  pollingTask: function(){
    let isVisible = !document.hidden, // check is user has switched to another tab browser
      isFocused = document.hasFocus(), // check is user has minimized browser window
      isIntersecting = this.isIntersecting; // switch to other application tab
    if(isIntersecting && isVisible && isFocused){ // check is user has switched to another tab or minimized browser window
      this.updateStatuses();
    }
  },
  //
  disableHandler: function(state){
    var isVisible = !document.hidden, // check is user has switched to another tab browser
      isIntersecting = this.isIntersecting; // switch to other application tab
    if(this.pollingTaskId && isIntersecting && isVisible){
      this.setContainerDisabled(state);
      this.pollingTask();
    }
  },
  //
  setContainerDisabled: function(state){
    let icon;
    this.mapPanel.setDisabled(state);
    if(state){
      icon = this.generateIcon(true, "stop-circle-o", "grey", __("suspend"));
    } else{
      icon = this.generateIcon(true, "circle", NOC.colors.yes, __("online"));
    }
    this.getViewModel().set("icon", icon);
  },
  subscribeToEvents: function(){
    window.addEventListener("focus", this.handleWindowFocus.bind(this));
    window.addEventListener("blur", this.handleWindowBlur.bind(this));
  },
  unsubscribeFromEvents: function(){
    window.removeEventListener("focus", this.handleWindowFocus.bind(this));
    window.removeEventListener("blur", this.handleWindowBlur.bind(this));
  },
  //
  destroy: function(){
    this.unsubscribeFromEvents();
    this.stopPolling();
    this.setContainerDisabled(false);
  },
  //
  handleWindowFocus: function(){
    setTimeout(function(me){
      me.disableHandler(false);
    }, 100, this);
  },
  //
  handleWindowBlur: function(){
    this.disableHandler(true);
  },
  //
  getVisibleFeaturesInLayer: function(layer){
    let bounds = this.map.getBounds(),
      visibleFeatures = [];
    if(layer && this.map.hasLayer(layer) && Ext.isFunction(layer.eachLayer)){
      layer.eachLayer(function(feature){
        var latlng = feature.getLatLng ? feature.getLatLng() : feature.getBounds().getCenter();
        if(bounds.contains(latlng)){
          visibleFeatures.push({
            id: feature.feature.id,
            properties: feature.feature.properties,
            coordinates: latlng,
            leafletLayer: feature,
          });
        }
      });
    }
    return visibleFeatures;
  },
  //
  getVisibleResources: function(){
    let resources = {};
    this.map.eachLayer(layer => {
      this.getVisibleFeaturesInLayer(layer)
        .filter(feature => feature.properties?.resource)
        .forEach(feature => {
          resources[feature.properties.resource] = feature;
        })
    });
    return resources;
  },
  //
  createStatusIcon: function(status, marker){
    let iconHtml,
      fontSize = marker.options?.icon?.options?.fontSize || 16
    switch(status){
      case "alarm":
      case "critical":
        iconHtml = `<i class="fa fa-fire" style="color: red; font-size: ${fontSize}px;"></i>`;
        break;
      case "warning":
        iconHtml = `<i class="fa fa-exclamation-triangle" style="color: orange; font-size: ${fontSize}px;"></i>`;
        break;
      case "down":
        iconHtml = `<i class="fa fa-times-circle" style="color: red; font-size: ${fontSize}px;"></i>`;
        break;
      case "up":
        iconHtml = `<i class="fa fa-check-circle" style="color: green; font-size: ${fontSize}px;"></i>`;
        break;
      default:
        iconHtml = `<i class="fa fa-circle" style="color: grey; font-size: ${fontSize}px;"></i>`;
    }
  
    return L.divIcon({
      ...marker.options?.icon?.options,
      html: iconHtml,
    });
  },
});
