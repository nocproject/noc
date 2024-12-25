//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.grids.SidebarController");

Ext.define("NOC.fm.alarm.view.grids.SidebarController", {
  extend: "Ext.app.ViewController",
  alias: "controller.fm.alarm.sidebar",
  pollingTaskId: undefined,
  pollingInterval: 12000,
  init: function(view){
    this.observer = new IntersectionObserver(function(entries){
      view.isIntersecting = entries[0].isIntersecting;
    }, {
      threshold: 1.0,
    });
    this.callParent();
  },
  //
  onResetFilter: function(){
    this.fireViewEvent("fmAlarmResetFilter");
  },
  //
  onSoundToggle: function(self, pressed){
    this.getViewModel().set("volume", pressed);
  },
  //
  onAutoReloadToggle: function(self, pressed){
    this.getViewModel().set("autoReload", pressed);
    this.setContainerDisabled(false);
    if(pressed){
      this.startPolling();
    } else{
      this.stopPolling();
    }
  },
  //
  startPolling: function(){
    this.observer.observe(this.getView().getEl().dom);
    if(this.pollingTaskId){
      this.pollingTask();
    } else{
      this.pollingTaskId = Ext.TaskManager.start({
        run: this.pollingTask,
        interval: this.pollingInterval,
        scope: this,
      });
    }
  },
  //
  stopPolling: function(){
    if(this.pollingTaskId){
      Ext.TaskManager.stop(this.pollingTaskId);
      this.pollingTaskId = undefined;
    }
  },
  //
  pollingTask: function(){
    var app = this.getView().up("[itemId=fm-alarm]"),
      gridsContainer = this.getView().up("[itemId=fm-alarm-list]"),
      isVisible = !document.hidden,
      isFocused = document.hasFocus(),
      isIntersecting = this.getView().isIntersecting;
    
    console.log("Polling Task ...", isVisible, isIntersecting, isFocused);
    // lib visibilityJS
    if(isIntersecting && isVisible && isFocused){ // check is user has switched to another tab or minimized browser window
      this.setContainerDisabled(false);
      // Check for new alarms and play sound
      this.checkNewAlarms();
      // Poll only application tab is visible
      if(!app.ownerCt.isVisible()){ // e.g. app.isActive()
        return;
      }
      // Poll only when in grid preview
      if(!gridsContainer.isVisible()){
        return;
      }
      // Poll only if polling is not locked
      if(this.isNotLocked(gridsContainer)){
        gridsContainer.down("[reference=fm-alarm-active]").getStore().reload();
        if(this.isRecentActive()){
          gridsContainer.down("[reference=fm-alarm-recent]").getStore().reload();
        }
      }
    } else{
      this.setContainerDisabled(true);
      console.log("disabled");
    }
  },
  setContainerDisabled: function(value){
    var app = this.getView().up("[itemId=fm-alarm]"),
      vm = app.getViewModel();
    vm.set("containerDisabled", value);
  },
  isRecentActive: function(){
    return this.getViewModel().get("recentFilter.cleared_after") > 0
  },
  isNotLocked: function(container){
    var viewTable = container.down("[reference=fm-alarm-active]").getView(),
      buttonPressed = this.getViewModel().get("autoReload"),
      isNotScrolling = viewTable.getScrollable().getPosition().y === 0,
      contextMenuHidden = viewTable.isHidden();
    return buttonPressed && isNotScrolling && contextMenuHidden;
  },
  //
  checkNewAlarms: function(){
    var ts, delta;
    ts = new Date().getTime();
    if(this.lastCheckTS && this.getViewModel().get("volume")){
      delta = Math.ceil((ts - this.lastCheckTS) / 1000.0);
      Ext.Ajax.request({
        url: "/fm/alarm/notification/?delta=" + delta,
        scope: this,
        success: function(response){
          var data = Ext.decode(response.responseText);
          if(data.sound){
            Ext.applyIf(this, {sounds: {} });
            this.sounds[data.sound] = new Audio(data.sound);
            this.sounds[data.sound].volume = data.volume || 1.0;
            this.sounds[data.sound].play();
          }
        },
      });
    }
    this.lastCheckTS = ts;
  },
  onResetStatuses: function(){
    this.fireViewEvent("fmAlarmSidebarResetSelection");
  },
});
