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

    this._windowFocused = document.hasFocus();

    this._handleWindowFocus = () => {
      if(this.destroyed) return;
      this._windowFocused = true;
      setTimeout(() => { if(!this.destroyed) this.disableHandler(false); }, 100);
    };
    this._handleWindowBlur = () => {
      if(this.destroyed) return;
      if(this.isFullScreen()) return;
      this._windowFocused = false;
      this.disableHandler(true);
    };
    this._handleVisibilityChange = () => {
      if(this.destroyed) return;
      this.disableHandler(document.hidden);
    };
    window.addEventListener("focus", this._handleWindowFocus);
    window.addEventListener("blur", this._handleWindowBlur);
    document.addEventListener("visibilitychange", this._handleVisibilityChange);

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

  isFullScreen: function(){
    return window.outerWidth === screen.width && window.outerHeight === screen.height;
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
    if(this._handleWindowFocus){
      window.removeEventListener("focus", this._handleWindowFocus);
      window.removeEventListener("blur", this._handleWindowBlur);
      document.removeEventListener("visibilitychange", this._handleVisibilityChange);
      this._handleWindowFocus = null;
      this._handleWindowBlur = null;
      this._handleVisibilityChange = null;
      this._windowFocused = false;
    }
  },

  isFocused: function(){
    return this._windowFocused;
  },

  disableHandler: function(state){
    if(this.destroyed) return;
    if(Ext.isFunction(this.setContainerDisabled)){
      this.setContainerDisabled(state);
    }
    if(!state && !document.hidden && this.isIntersecting){
      this.pollingTask();
    }
  },

  pollingTask: Ext.emptyFn,

  generateIcon: function(isUpdatable, icon, color, msg){
    if(isUpdatable){
      return `<i class='fa fa-${icon}' style='color:${color};width:16px;' data-qtip='${msg}'></i>`;
    }
    return "<i class='fa fa-fw' style='width:16px;'></i>";
  },
});
