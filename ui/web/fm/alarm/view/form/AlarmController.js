//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.form.AlarmController");

Ext.define("NOC.fm.alarm.view.form.AlarmController", {
  extend: "Ext.app.ViewController",
  alias: "controller.fm.alarm.form",
  plugins: [],
  selectedBinding: undefined,
  initViewModel: function(viewModel){
    this.selectedBinding = viewModel.bind({
      bindTo: "{selected}",
      deep: true,
    }, this.onChangeSelected, this);
  },
  destroy: function(){
    this.selectedBinding.destroy();
  },
  onChangeSelected: function(data){
    var tabPanel = this.getView().down("[reference=fm-alarm-form-tab-panel]");
    // Remove plugins
    if(this.plugins.length){
      Ext.each(this.plugins, function(p){
        tabPanel.remove(p);
      });
      this.plugins = [];
    }
    // Install plugins
    if(data.plugins && !this.plugins.length){
      Ext.each(data.plugins, function(v){
        var cls = v[0],
          config = {
            app: this.getView().up("[itemId=fm-alarm]"),
            data: data,
          },
          p;
        Ext.apply(config, v[1]);
        p = Ext.create(cls, config);
        this.plugins.push(p);
        tabPanel.add(p);
        p.updateData(data);
      }, this);
    }
  },
  onClose: function(){
    this.fireViewEvent("fmAlarmCloseForm");
  },
  onRefreshForm: function(){
    this.fireViewEvent("fmAlarmRefreshForm");
  },
  onEscalateObject: function(){
    Ext.Ajax.request({
      url: "/fm/alarm/escalate/",
      method: "POST",
      jsonData: {
        ids: [this.getViewModel().get("selected.id")],
      },
      scope: this,
      success: function(response){
        var data = Ext.decode(response.responseText);
        if(data.status){
          NOC.info(__("Escalated"));
        } else{
          NOC.error(__("Escalate failed : ") + (Object.prototype.hasOwnProperty.call(data, "error") ? data.error : "unknowns error!"));
        }
      },
      failure: function(){
        NOC.error(__("Escalate failed"));
      },
    });
  },
  onShowCard: function(){
    window.open(
      "/api/card/view/alarm/" + this.getViewModel().get("selected.id") + "/",
    );
  },
  onShowObject: function(){
    NOC.launch("sa.managedobject", "history", {
      args: [this.getViewModel().get("selected.managed_object")],
    });

  },
  onClear: function(){
    Ext.MessageBox.prompt(
      __("Clear alarm?"),
      __("Please confirm the alarm is closed and must be cleared?"),
      function(btn, text){
        if(btn === "ok"){
          Ext.Ajax.request({
            url: "/fm/alarm/" + this.getViewModel().get("selected.id") + "/clear/",
            method: "POST",
            jsonData: {
              msg: text,
            },
            scope: this,
            success: function(){
              NOC.info(__("Alarm cleared"))
            },
            failure: function(){
              NOC.error(__("Failed to clear alarm"));
            },
          });
        }
      },
      this,
    );
  },
  onWatch: function(self){
    var cmd = self.pressed ? "/subscribe/" : "/unsubscribe/";
    Ext.Ajax.request({
      url: this.getViewModel().get("alarmUrl") + cmd,
      method: "POST",
      scope: this,
      success: Ext.emptyFn,
      failure: function(){
        NOC.error(__("Failed to set watcher"));
      },
    })
  },
  onAcknowledge: function(self){
    var ackUser = self.pressed ? NOC.username : null,
      alarmId = this.getViewModel().get("selected").id,
      appController = this.getView().up("[itemId=fm-alarm]").getController(),
      // arrow function to keep the context
      successFn = (status) =>{
        if(status){
          this.getViewModel().set("selected.ack_user", ackUser);
          this.fireViewEvent("fmAlarmRefreshForm");
        }
      };
    appController.acknowledgeDialog(alarmId, !self.pressed, successFn);
  },
  onSetRoot: function(){
    Ext.MessageBox.prompt(
      __("Set root"),
      __("Please enter root cause alarm id"),
      function(btn, text){
        if(btn === "ok"){
          // @todo: Check alarm id
          Ext.Ajax.request({
            url: this.getViewModel().get("alarmUrl") + "/set_root/",
            method: "POST",
            scope: this,
            jsonData: {
              root: text,
            },
            success: function(){
              this.onRefresh();
            },
            failure: function(){
              NOC.error(__("Failed to set root cause"));
            },
          });
        }
      },
      this,
    );
  },
  onMessageKey: function(field, key){
    switch(key.getKey()){
      case Ext.EventObject.ENTER:
        key.stopEvent();
        this.submitMessage(field);
        break;
      case Ext.EventObject.ESC:
        key.stopEvent();
        field.setValue("");
        break;
    }
  },
  onRenderStatus: function(value){
    return NOC.render.Choices({
      A: "Active",
      C: "Archived",
    })(value);
  },
  submitMessage: function(field){
    if(!field.getValue())
      return;
    Ext.Ajax.request({
      url: this.getViewModel().get("alarmUrl") + "/post/",
      method: "POST",
      scope: this,
      jsonData: {
        msg: field.getValue(),
      },
      success: function(){
        var store = this.getView().lookupReference("fm-alarm-log").getStore(),
          status = this.getViewModel().get("selected.status");
        store.add({
          timestamp: new Date(),
          from_status: status,
          to_status: status,
          message: field.getValue(),
        });
        field.setValue("");
      },
      failure: function(){
        NOC.error(__("Failed to post message"));
      },
    });
  },
  onRowDblClickTreePanel: function(grid, record){
    this.fireViewEvent("fmAlarmSelectItem", record);
  },
  onAddRemoveFav: function(){
    var currentId = this.getViewModel().get("selected.id"),
      fav_status = this.getViewModel().get("selected.fav_status"),
      action = fav_status ? "reset" : "set",
      url = "/fm/alarm/favorites/item/" + currentId + "/" + action + "/";
    Ext.Ajax.request({
      url: url,
      method: "POST",
      scope: this,
      success: function(){
        var vm = this.getViewModel();
        // Invert current status
        vm.set("selected.fav_status", !fav_status);
      },
    });
  },
});
