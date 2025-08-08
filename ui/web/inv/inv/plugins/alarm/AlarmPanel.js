//---------------------------------------------------------------------
// inv.inv Alarm Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.alarm.AlarmPanel");

Ext.define("NOC.inv.inv.plugins.alarm.AlarmPanel", {
  extend: "Ext.panel.Panel",
  requires: [
    "NOC.inv.inv.plugins.alarm.AlarmModel",
  ],
  pollingTaskId: undefined,
  pollingInterval: 5000,
  // ViewModel for this panel
  viewModel: {
    data: {
      objectId: null,
      autoReload: false,
      autoReloadIcon: "xf05e", // NOC.glyph.ban
      autoReloadText: __("Auto reload : OFF"),
      icon: "<i class='fa fa-fw' style='width:16px;'></i>",
    },
  },
  //
  title: __("Alarms"),
  closable: false,
  layout: "fit",
  //
  initComponent: function(){
    var me = this;

    me.defaultRoot = {
      text: __("."),
      children: [],
    };

    me.store = Ext.create("Ext.data.TreeStore", {
      model: "NOC.inv.inv.plugins.alarm.AlarmModel",
      root: me.defaultRoot,
    });

    me.alarmPanel = Ext.create("Ext.tree.Panel", {
      store: me.store,
      rootVisible: false,
      useArrows: true,
      stateful: true,
      stateId: "inv.inv-alarm-alarm",
      emptyText: __("No Alarms"),
      tbar: [
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
      columns: [
        {
          xtype: "treecolumn",
          dataIndex: "title",
          text: __("Title"),
          width: 400,
        },
        {
          text: __("Alarm Class"),
          dataIndex: "alarm_class",
          width: 300,
          renderer: NOC.render.Lookup("alarm_class"),
        },
        {
          text: __("Severity"),
          dataIndex: "severity",
          width: 70,
          renderer: function(v, _, record){
            return record.get("severity__label") +
              "<br/>" +
              record.get("severity");
          },
        },
        {
          text: __("Time/Duration"),
          dataIndex: "timestamp",
          width: 120,
          renderer: function(v, _, record){
            return NOC.render.DateTime(record.get("timestamp")) +
              "<br/>" +
              NOC.render.Duration(record.get("duration"));
          },
        },
        {
          text: __("Channel"),
          dataIndex: "channel",
          width: 300,
          renderer: function(v, _, record){
            let html = "<span",
              channelId = record.get("channel"),
              channelLabel = record.get("channel__label") || v || "";
            if(!Ext.isEmpty(channelId)){
              html += ` class="noc-clickable-object noc-channel"  data-object-id="${channelId}"`;
            }
            return html + `>${channelLabel}</span>`;
          },
        },
        {
          text: __("Object"),
          dataIndex: "object",
          flex: 1,
          renderer: function(v){
            if(v && v.length > 0){
              return v.map(function(x){
                let html = "<span";
                if(!Ext.isEmpty(x.id)){
                  html += ` class="noc-clickable-object noc-object"  data-object-id="${x.id}"`;
                }
                return html + `>${x.title}</span>`;
              }).join(" > ");
            }
            return "";
          },  
        },
      ],
      viewConfig: {
        getRowClass: Ext.bind(me.getRowClass, me),
      },
      listeners: {
        scope: this,
        afterrender: function(panel){
          panel.getEl().on("click", function(e, target){
            var objectId = target.getAttribute("data-object-id");
            if(objectId && target.classList.contains("noc-object")){
              if(e.shiftKey){
                NOC.launch("inv.inv", "history", {
                  args: [objectId],
                });

              } else{
                this.up("[appId]").showObject(objectId);
              }
            }
            if(objectId && target.classList.contains("noc-channel")){
              NOC.launch("inv.channel", "history", {
                args: [objectId],
                "override": [
                  {
                    "showGrid": function(){
                      this.up().close();
                    },
                  },
                ],
              });
            }
          }, this, {
            delegate: ".noc-clickable-object",
            stopEvent: true,
          });
        },
      },
    });
    //
    Ext.apply(me, {
      items: [
        me.alarmPanel,
      ],
    });
    me.callParent();
    this.subscribeToEvents();
  },
  //
  preview: function(data, objectId){
    var me = this;
    this.getViewModel().set("objectId", objectId);
    me.store.setRootNode(data || me.defaultRoot);
  },
  // Return Grid's row classes
  getRowClass: function(record){
    var c = record.get("row_class");
    if(c){
      return c;
    } else{
      return "";
    }
  },
  //
  onAutoReloadToggle: function(self){
    this.getViewModel().set("autoReload", self.pressed);
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
    var me = this;
    
    if(this.observer){
      this.stopPolling();
    }
    
    this.observer = new IntersectionObserver(function(entries){
      if(me.destroyed) return;
      me.isIntersecting = entries[0].isIntersecting;
      me.disableHandler(!entries[0].isIntersecting);
    }, {
      threshold: 0.1,
    });
    
    if(this.getEl() && this.getEl().dom){
      this.observer.observe(this.getEl().dom);
    }
    
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
    if(this.observer && this.getEl() && this.getEl().dom){
      this.observer.unobserve(this.getEl().dom);
      this.observer.disconnect();
      this.observer = null;
    }
  },
  //
  pollingTask: function(){
    if(this.destroyed) return;
    
    let isVisible = !document.hidden, // check is user has switched to another tab browser
      isFocused = document.hasFocus(), // check is user has minimized browser window
      isIntersecting = this.isIntersecting; // switch to other application tab
    if(isIntersecting && isVisible && isFocused){ // check is user has switched to another tab or minimized browser window
      console.log("Polling task executed");
      this.alarmUpdate();
    }
  },
  //
  disableHandler: function(state){
    if(this.destroyed) return;
    
    var isVisible = !document.hidden, // check is user has switched to another tab browser
      isIntersecting = this.isIntersecting; // switch to other application tab
    if(this.pollingTaskId && isIntersecting && isVisible){
      this.setContainerDisabled(state);
      this.pollingTask();
    }
  },
  //
  setContainerDisabled: function(state){
    if(this.destroyed) return;
    
    let icon;
    this.alarmPanel.setDisabled(state);
    if(state){
      icon = this.generateIcon(true, "stop-circle-o", "grey", __("suspend"));
    } else{
      icon = this.generateIcon(true, "circle", NOC.colors.yes, __("online"));
    }
    if(this.getViewModel()){
      this.getViewModel().set("icon", icon);
    }
  },
  subscribeToEvents: function(){
    this.handleWindowFocus = this.handleWindowFocus.bind(this);
    this.handleWindowBlur = this.handleWindowBlur.bind(this);
    window.addEventListener("focus", this.handleWindowFocus);
    window.addEventListener("blur", this.handleWindowBlur);
  },
  
  unsubscribeFromEvents: function(){
    if(this.handleWindowFocus){
      window.removeEventListener("focus", this.handleWindowFocus);
    }
    if(this.handleWindowBlur){
      window.removeEventListener("blur", this.handleWindowBlur);
    }
  },
  //
  destroy: function(){
    this.destroyed = true;
    
    this.unsubscribeFromEvents();
    this.stopPolling();
    this.setContainerDisabled(false);
    
    this.isRefreshing = false;
    this.isUpdating = false;
    
    this.callParent();
  },
  //
  handleWindowFocus: function(){
    if(this.destroyed) return;
    var me = this;
    setTimeout(function(){
      if(!me.destroyed){
        me.disableHandler(false);
      }
    }, 100);
  },
  //
  handleWindowBlur: function(){
    if(this.destroyed) return;
    this.disableHandler(true);
  },
  //
  alarmUpdate: function(){
    let objectId = this.getViewModel().get("objectId");
    if(Ext.isEmpty(objectId)){
      return;
    }
    if(this.destroyed || this.isUpdating) return;
    
    this.isUpdating = true;
    
    this.getViewModel().set("icon", this.generateIcon(true, "spinner", "grey", __("loading")));
    
    Ext.Ajax.request({
      url: `/inv/inv/${objectId}/plugin/alarm/`,
      method: "GET",
      scope: this,
      success: function(response){
        if(this.destroyed) return;
        let data = Ext.decode(response.responseText);
        this.preview(data, objectId);
      },
      failure: function(){
        if(!this.destroyed){
          NOC.error(__("Failed to update alarm"));
        }
      },
      callback: function(){
        if(!this.destroyed){
          this.getViewModel().set("icon", this.generateIcon(true, "circle", NOC.colors.yes, __("online")));
          this.isUpdating = false;
        }
      },
    });
  },
});