//---------------------------------------------------------------------
// Application UI
//---------------------------------------------------------------------
// Copyright (C) 2007-2024d The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC application");

Ext.application({
  name: "NOC",
  paths: {
    "NOC": "/ui/web",
    "Ext.ux": "/ui/web/ux",
  },

  requires: [
    "NOC.main.desktop.Application",
    "NOC.main.desktop.LoginView",
  ],

  launch: function(){
    Ext.Ajax.request({
      url: "/api/login/is_logged/",
      method: "GET",
      scope: this,
      success: function(response){
        if(Ext.decode(response.responseText)){
          this.openApplication();
          return;
        }

        var hash = location.hash,
          newUrl = location.protocol + "//" + 
                      location.host + 
            "?uri=/" + hash;

        history.replaceState({}, document.title, newUrl);
        this.openLogin();
      },
      failure: function(response){
        console.error("Request failed:", response.status);
      },
    });
  },
  openApplication: function(){
    Ext.setGlyphFontFamily("FontAwesome");
    console.log("Initializing history API");
    Ext.History.init();
    console.log("NOC application starting");
    this.settings();
  },
  openLogin: function(){
    console.log("NOC login starting");
    Ext.create("NOC.main.desktop.LoginView", {
      listeners: {
        scope: this,
        afterRender: this.hideSplashScreen,
      },
    });
    console.log("NOC login started");
  },
  settings: function(){
    Ext.Ajax.request({
      url: "/main/desktop/settings/",
      method: "GET",
      scope: this,
      success: function(response){
        var setup = Ext.decode(response.responseText);
        console.log("!!!");
        console.log("!!! Running NOC desktop");
        console.log("!!!");
        // Initialize loader
        Ext.BLANK_IMAGE_URL = "/ui/web/img/s.gif";
        NOC.settings = {
          systemId: setup.system_uuid ? setup.system_uuid : null,
          brand: setup.brand,
          installation_name: setup.installation_name,
          preview_theme: setup.preview_theme,
          language: setup.language,
          logo_url: setup.logo_url,
          logo_width: setup.logo_width,
          logo_height: setup.logo_height,
          branding_color: setup.branding_color,
          branding_background_color: setup.branding_background_color,
          enable_search: setup.enable_search,
          gitlab_url: setup.gitlab_url,
          collections: {
            allow_sharing: setup.collections.allow_sharing,
            allow_overwrite: setup.collections.allow_overwrite,
            project_id: setup.collections.project_id,
          },
          gis: {
            base: {
              enable_blank: setup.gis.base.enable_blank,
              "enable_osm": setup.gis.base.enable_osm,
              "enable_google_roadmap": setup.gis.base.enable_google_roadmap,
              "enable_google_hybrid": setup.gis.base.enable_google_hybrid,
              "enable_google_sat": setup.gis.base.enable_google_sat,
              "enable_google_terrain": setup.gis.base.enable_google_terrain,
              "enable_tile1": setup.gis.base.enable_tile1,
              "enable_tile2": setup.gis.base.enable_tile2,
              "enable_tile3": setup.gis.base.enable_tile3,
              "enable_yandex_roadmap": setup.gis.base.enable_yandex_roadmap,
              "enable_yandex_hybrid": setup.gis.base.enable_yandex_hybrid,
              "enable_yandex_sat": setup.gis.base.enable_yandex_sat,
            },
            custom: {
              tile1: {
                name: setup.gis.custom.tile1.name,
                url: setup.gis.custom.tile1.url,
                subdomains: setup.gis.custom.tile1.subdomains,
              },
              tile2: {
                name: setup.gis.custom.tile2.name,
                url: setup.gis.custom.tile2.url,
                subdomains: setup.gis.custom.tile2.subdomains,
              },
              tile3: {
                name: setup.gis.custom.tile3.name,
                url: setup.gis.custom.tile3.url,
                subdomains: setup.gis.custom.tile3.subdomains,
              },
            },
            "yandex_supported": setup.gis.yandex_supported,
            default_layer: setup.gis.default_layer,
          },
          traceExtJSEvents: setup.traceExtJSEvents,
          helpUrl: setup.helpUrl,
          helpBranch: setup.helpBranch,
          helpLanguage: setup.helpLanguage,
          timezone: setup.timezone,
          enable_remote_system_last_extract_info: setup.enable_remote_system_last_extract_info,
          enableHelp: setup.helpUrl && setup.helpUrl !== "",
          has_geocoder: setup.has_geocoder,
        };
        NOC.templates = {};
        // Change title
        document.title = setup.brand + "|" + setup.installation_name;
        // Add favicon
        if(setup.favicon_mime){
          var link = document.createElement("link");
          link.rel = "icon";
          link.type = setup.favicon_mime;
          link.href = setup.favicon_url;
          document.head.appendChild(link);
        }
        Ext.Loader.loadScript({
          url: "/ui/web/js/override.js",
          onLoad: function(){
            // Create viewport after overrides loaded
            this.app = Ext.create("NOC.main.desktop.Application", {
              listeners: {
                scope: this,
                applicationReady: this.hideSplashScreen,
              },
            });
          },
          onError: function(){
            NOC.error(__("Failed to load override.js"));
          },
          scope: this,
        });
      },
      failure: function(response){
        console.error("Request failed:", response.status);
      },
    });
  },
  hideSplashScreen: function(){
    var mask = Ext.get("noc-loading-mask"),
      parent = Ext.get("noc-loading");
    mask.fadeOut({
      callback: function(){
        mask.destroy();
      },
    });
    parent.fadeOut({
      callback: function(){
        parent.destroy();
      },
    });
  },
});
