//---------------------------------------------------------------------
// Polling mixin
// Provides Ext.TaskManager polling with IntersectionObserver visibility guard.
// Host class must define:
//   - pollingInterval {Number} — poll period in ms
//   - pollingTask {Function} — called each interval when visible (override in host class)
// Optional host class methods:
//   - setContainerDisabled(state) — called by disableHandler when visibility changes
//---------------------------------------------------------------------
// Copyright (C) 2007-2026 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.mixins.Polling");

Ext.define("NOC.core.mixins.Polling", {
  isIntersecting: false,
  pollingTaskId: undefined,
  observer: null,

  startPolling: function(){
    if(this.observer){
      this.stopPolling();
    }

    this.observer = new IntersectionObserver((entries) => {
      if(this.destroyed) return;
      this.isIntersecting = entries[0].isIntersecting;
      this.disableHandler(!entries[0].isIntersecting);
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

  stopPolling: function(){
    if(this.pollingTaskId){
      Ext.TaskManager.stop(this.pollingTaskId);
      this.pollingTaskId = undefined;
    }
    if(this.observer){
      if(this.getEl() && this.getEl().dom){
        this.observer.unobserve(this.getEl().dom);
      }
      this.observer.disconnect();
      this.observer = null;
    }
  },

  disableHandler: function(state){
    if(this.destroyed) return;
    var isVisible = !document.hidden,
      isIntersecting = this.isIntersecting;
    if(this.pollingTaskId && isIntersecting && isVisible){
      if(Ext.isFunction(this.setContainerDisabled)){
        this.setContainerDisabled(state);
      }
      this.pollingTask();
    }
  },

  pollingTask: Ext.emptyFn,
});
