//---------------------------------------------------------------------
// main.desktop application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.desktop.Application");
Ext.define("NOC.main.desktop.Application", {
  extend: "Ext.Viewport",
  layout: "border",
  requires: [
    "NOC.core.InactivityLogout",
    "NOC.core.PasswordField",
    "NOC.core.ObservableModel",
    "NOC.core.Observable",
    "NOC.core.TagsField",
    "NOC.core.StringListField",
    "NOC.core.StateField",
    "NOC.core.StateProvider",
    "NOC.main.desktop.WorkplacePanel",
    "NOC.main.desktop.HeaderPanel",
    "NOC.main.desktop.NavPanel",
    "NOC.main.desktop.Breadcrumbs",
    "Ext.ux.form.SearchField",
    "Ext.ux.form.GridField",
    "Ext.ux.form.DictField",
    "Ext.ux.form.ColorField",
    "Ext.ux.grid.column.GlyphAction",
  ],

  initComponent: function(){
    var me = this;
    // initial permissions cache

    NOC.permissions$ = new NOC.core.Observable({model: new NOC.core.ObservableModel});
    NOC.restartReason = null;
    me.templates = NOC.templates["main_desktop"];
    // Setup helpers
    NOC.run = Ext.bind(me.launchTab, me);
    NOC.launch = Ext.bind(me.launchApp, me);
    //
    me.launchedTabs = {};
    //
    me.navStore = Ext.create("Ext.data.TreeStore", {
      root: {
        id: "root",
        text: __("All"),
        expanded: true,
        children: [{
          text: "[HIDDEN] Row height measurement node",
          leaf: true, 
          measurementNode: true,
        }],
      },
    });
    // Create panels
    me.headerPanel = Ext.create("NOC.main.desktop.HeaderPanel", {app: me});
    me.navPanel = Ext.create("NOC.main.desktop.NavPanel", {
      app: me,
      store: me.navStore,
    });
    me.breadcrumbs = Ext.create("NOC.main.desktop.Breadcrumbs", {
      app: me,
      store: me.navStore,
    });
    me.workplacePanel = Ext.create("NOC.main.desktop.WorkplacePanel", {app: me});
    //
    Ext.apply(me, {
      items: [
        me.headerPanel,
        me.breadcrumbs,
        me.navPanel,
        me.workplacePanel,
      ],
    });
    me.callParent();
    // Set unload handler
    me.boundOnUnload = me.onUnload.bind(me);
    window.addEventListener("beforeunload", me.boundOnUnload);
  },
  //
  afterRender: function(){
    this.callParent();
    this.onLogin();
    this.fireEvent("applicationReady");
    console.log("NOC application ready");
  },
  // Launch applications from URL or home
  launchApps: function(){
    var hash = Ext.History.getHash();
    if(hash){ // Open application tab
      var paths = hash.split("/").filter(Boolean),
        app = paths.shift();
      if(paths.length > 0){
        NOC.launch(app, "history", {args: paths});
      } else{
        NOC.launch(app);
      }
    } else{ // Launch home application
      this.launchTab("NOC.main.home.Application", "Home", {});
    }
  },
  // Show About screen
  onAbout: function(){
    var me = this;
    Ext.Ajax.request({
      url: "/main/desktop/about/",
      method: "GET",
      scope: me,
      success: function(response){
        var data = Ext.decode(response.responseText);
        Ext.create("NOC.main.desktop.About", {
          app: me,
          aboutCfg: data,
        });
      },
      failure: function(){
        NOC.error(__("Failed to get data"));
      },
    });
  },
  // Launch application from navigation record
  launchRecord: function(record, reuse){
    var li;
    if(!record.isLeaf()){
      return;
    }
    li = record.get("launch_info");
    if(li.params && li.params.link){
      window.open(li.params.link);
    } else{
      this.launchTab(
        li.class, li.title, li.params, record.get("id"), reuse,
      );
    }
  },
  // Launch application in tab
  launchTab: function(panel_class, title, params, node, reuse){
    var paths;
    if(reuse && node && this.launchedTabs[node]){
      // Open tab
      this.workplacePanel.setActiveTab(this.launchedTabs[node]);
    } else{
      if(title !== "Home"){
        NOC.msg.started(__("Starting \"{0}\""), title);
      }
      // Launch new tab
      if(!params.app_id){
        paths = panel_class.split(".");
        params.app_id = [paths[1], paths[2]].join(".");
      }
      this.workplacePanel.launchTab(panel_class, title, params, node);
    }
  },
  launchApp: function(app, cmd, data){
    var me = this;
    // iframe shortcut
    if(app === "iframe"){
      me.launchTab(
        "NOC.main.desktop.IFramePanel",
        data.title,
        {url: data.url},
      );
      return;
    }
    //
    // skip saved hash
    var index = app.indexOf("?"),
      _app = index === -1 ? app : app.substr(0, index),
      url = "/" + _app.replace(".", "/") + "/launch_info/";
    Ext.Ajax.request({
      url: url,
      method: "GET",
      scope: me,
      success: function(response){
        var li = Ext.decode(response.responseText),
          params = {filterValuesUrl: app};
        if(cmd){
          params.cmd = Ext.merge({}, data);
          params.cmd.cmd = cmd;
        }
        Ext.merge(params, li.params);
        me.launchTab(
          li.class,
          li.title,
          params,
        );
        // restore saved hash
        if(index !== -1){
          Ext.History.setHash(app);
        }
      },
      failure: function(){
        NOC.error(__("Failed to launch application ") + " " + app);
      },
    });
  },
  // Called when application tab closed
  onCloseApp: function(menuId){
    var me = this;
    if(me.launchedTabs[menuId]){
      delete me.launchedTabs[menuId];
    }
  },
  // Search text entered
  onSearch: function(value){
    NOC.launch("main.search", "search", {query: value});
  },
  // Toggle all panels except workplace
  onPanelsToggle: function(){
    var me = this;
    if(me.headerPanel.isHidden()){
      me.headerPanel.show();
      me.navPanel.show();
      me.workplacePanel.setCollapsed();
    } else{
      me.headerPanel.hide();
      me.navPanel.hide();
      me.workplacePanel.setExpanded();
    }
  },
  // Show user profile panel
  onUserProfile: function(){
    NOC.run(
      "NOC.main.userprofile.Application",
      "User Profile",
      {},
    );
  },
  // Show change credentials form
  onChangeCredentials: function(){
    var me = this;
    Ext.create("NOC.main.desktop.ChangeCredentials", {
      app: me,
      fields: [
        {
          xtype: "textfield",
          name: "old_password",
          fieldLabel: __("Old Password"),
          allowBlank: false,
          inputType: "password",
        },

        {
          xtype: "textfield",
          name: "new_password",
          fieldLabel: __("New Password"),
          allowBlank: false,
          inputType: "password",
        },

        {
          xtype: "textfield",
          name: "retype_password",
          fieldLabel: __("Retype New Password"),
          allowBlank: false,
          inputType: "password",
          vtype: "password",
          peerField: "new_password",
        },
      ],
    });
  },
  // Called when session is authenticated or user logged in
  onLogin: async function(){
    // Initialize state provider
    const provider = new NOC.core.StateProvider();
    await provider.loadState();
    Ext.state.Manager.setProvider(provider);
    console.log("User preferences state: ", provider.state);
    this.launchApps();
    // Apply user settings
    Ext.Ajax.request({
      method: "GET",
      url: "/main/desktop/user_settings/",
      async: true, // make one request, when reload with open tab
      scope: this,
      success: function(response){
        var settings = Ext.decode(response.responseText),
          displayName = [];
        // Save settings
        NOC.username = settings.username;
        NOC.email = settings.email;
        // Build display name
        if(settings.first_name){
          displayName.push(settings.first_name);
        }
        if(settings.last_name){
          displayName.push(settings.last_name);
        }
        if(displayName.length === 0){
          displayName.push(settings.username);
        }
        this.headerPanel.setUserName(displayName.join(" "));
        // Display username button
        this.headerPanel.showUserMenu(settings.can_change_credentials);
        // Reset opened tabs
        this.launchedTabs = {};
        // Set menu
        this.navStore.setRoot(settings.navigation);
        this.breadcrumbs.updateSelection("root");
        // Setup idle timer
        NOC.core.InactivityLogout.init(settings.idle_timeout);
        // permissions cache
        NOC.permissions$.next(this.getPermissions(settings.navigation.children));
        NOC.info_icon("fa-sign-in", __("Logged in as ") + settings.username);
      },
      failure: function(){
        NOC.error(__("Failed to get user settings"));
      },
    });
  },
  //
  getPermissions: function(tree){
    var result = [],
      children = function(leaf){
        if(Object.prototype.hasOwnProperty.call(leaf, "launch_info")
          && Object.prototype.hasOwnProperty.call(leaf.launch_info, "params")
          && Object.prototype.hasOwnProperty.call(leaf.launch_info.params, "app_id")){
          result.push(
            new NOC.core.ObservableModel({
              key: leaf.launch_info.params.app_id,
              value: leaf.launch_info.params.permissions,
            }),
          );
        }
        if(Object.prototype.hasOwnProperty.call(leaf, "children") && leaf.children){
          Ext.Array.map(leaf.children, children);
        }
      };
    Ext.Array.map(tree, children);
    return result;
  },
  // Start logout sequence
  onLogout: function(msg){
    const url = "/api/login/logout/";
    if(msg === "Autologout"){
      window.removeEventListener("beforeunload", this.boundOnUnload);
      localStorage.setItem("NOC.restartReason", msg);
    }
    document.location = url;
  },
  //
  onUnload: function(e){
    if(NOC.restartReason){
      return;
    }
    if(this.hasUnsavedChanges()){
      // modern browsers no longer support custom messages in the unload dialog for security reasons 
      e.preventDefault();
      e.returnValue = "";
    }
  },
  //
  hasUnsavedChanges: function(){
    var forms = Ext.ComponentQuery.query("form"),
      isDirty = forms.some(function(form){
        return form.isDirty();
      });
    return isDirty;
  },
  //
  restartApplication: function(reason){
    NOC.restartReason = reason;
    window.location.reload();
  },
  // Request full-screen mode
  requestFullscreen: function(){
    var element = document.body,
      method = element.requestFullScreen
        || element.webkitRequestFullScreen
        || element.mozRequestFullScreen
        || element.msRequestFullScreen;
    if(method){
      method(element);
    }
  },
  exitFullscreen: function(){
    var method = document.exitFullScreen
      || document.webkitExitFullScreen
      || document.mozCancelFullScreen
      || document.msExitFullScreen;
    if(method){
      method();
    }
  },
  //
  toggleNav: function(){
    var me = this;
    if(me.breadcrumbs.isVisible()){
      me.breadcrumbs.hide();
      me.navPanel.show();
    } else{
      me.breadcrumbs.show();
      me.navPanel.hide();
    }
  },
  //
  setActiveNavTabTooltip: function(text){
    var me = this;
    Ext.each(me.workplacePanel.tabBar.getRefItems(), function(btn){
      if(btn.active === true){
        btn.setTooltip(text);
        return false;
      }
    });
  },
  //
  clearActiveNavTabTooltip: function(){
    var me = this;
    Ext.each(me.workplacePanel.tabBar.getRefItems(), function(btn){
      if(btn.active === true){
        btn.setTooltip(undefined);
        return false;
      }
    });
  },
});
