//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.debug('Defining NOC.sa.managedobject.form.FormController');
Ext.define('NOC.sa.managedobject.form.FormController', {
  extend: 'Ext.app.ViewController',
  requires: [
    "Ext.ux.grid.column.GlyphAction",
    "NOC.sa.managedobject.Model",
    "NOC.sa.managedobject.Proxy",
  ],
  alias: 'controller.managedobject.form',
  url: '/sa/managedobject/',

  init: function(app){
    var view = this.getView().up('[itemId=sa-managedobject]'),
      consoleBtn = app.down('[itemId=consoleBtn]'),
      deleteBtn = app.down('[itemId=deleteBtn]'),
      cmdBtn = app.down('[itemId=cmdBtn]'),
      scriptsBtn = app.down('[itemId=scriptsBtn]'),
      configBtn = app.down('[itemId=configBtn]'),
      confDBBtn = app.down('[itemId=confDBBtn]'),
      saveBtn = app.down('[itemId=saveBtn]'),
      resetBtn = app.down('[itemId=resetBtn]'),
      cloneBtn = app.down('[itemId=cloneBtn]'),
      alarmsBtn = app.down('[itemId=alarmsBtn]'),
      createBtn = app.down('[itemId=createBtn]'),
      stateField = app.down('[xtype=statefield]');

    // saveBtn.formBind = view.hasPermission("update");
    consoleBtn.setDisabled(!view.hasPermission("console"));
    deleteBtn.setDisabled(!view.hasPermission("delete"));
    cmdBtn.setDisabled(!view.hasPermission("interactions"));
    scriptsBtn.setDisabled(!view.hasPermission("script"));
    configBtn.setDisabled(!view.hasPermission("config"));
    confDBBtn.setDisabled(!view.hasPermission("config"));
    saveBtn.setDisabled(!view.hasPermission("update"));
    resetBtn.setDisabled(!view.hasPermission("update"));
    cloneBtn.setDisabled(!view.hasPermission("create"));
    alarmsBtn.setDisabled(!view.hasPermission("alarm"));
    createBtn.setDisabled(!view.hasPermission("create"));
    // customize style
    stateField.margin = this.getView().stateMargin;
    stateField.labelWidth = this.getView().stateLabelWidth;
  },
  toMain: function(){
    this.gotoItem('managedobject-select');
  },
  onSaveRecord: function(){
    var me = this.getView();
    if(!this.getView().down('[itemId=managedobject-form-panel]').form.isValid()){
      NOC.error(__("Error in data"));
      return;
    }
    var v = me.getFormData();
    // normalize custom fields
    Ext.each(me.up('[itemId=sa-managedobject]').noc.cust_form_fields, function(field){
      if(field.xtype === 'datefield' && !Ext.isEmpty(v[field.name])){
        v[field.name] = Ext.Date.format(v[field.name], field.altFormats);
      }
    })
    // ToDo remove id, when new record
    // if(!me.currentRecord && v[me.idField] !== undefined) {
    //     delete v[me.idField];
    // }
    //
    this.saveRecord(v);

  },
  onSaveRecords: function(){
    var me = this,
      values = {},
      formPanel = this.getView().down('[itemId=managedobject-form-panel]'),
      form = formPanel.getForm(),
      groupEditFields = Ext.Array.filter(form.getFields().items, function(field){return field.groupEdit}),
      valuesTxt = "";
    // @todo: Form validation
    Ext.Array.each(groupEditFields, function(field){
      if(Ext.isFunction(field.isDirty) && field.isDirty()){
        if(Ext.isFunction(field.getDisplayValue) && field.getDisplayValue() !== "Leave unchanged"){
          valuesTxt += (field.fieldLabel || field.name) + ": '" + field.getDisplayValue() + "'</br>";
        } else if(field.getValue() !== "Leave unchanged"){
          valuesTxt += (field.fieldLabel || field.name) + ": '" + field.getValue() + "'</br>";
        }
        if(field.getValue() !== "Leave unchanged" || field.getDisplayValue() !== "Leave unchanged"){
          values[field.name] = field.getValue();
        }
      }
    });
    if(!Ext.Object.isEmpty(values)){
      values.ids = formPanel.ids;
      var message = Ext.String.format("Do you wish to change {0} record(s): <br/><br/>{1}<br/>This operation cannot be undone!", values.ids.length, valuesTxt);
      Ext.Msg.show({
        title: __("Change records?"),
        msg: message,
        buttons: Ext.Msg.YESNO,
        icon: Ext.window.MessageBox.QUESTION,
        modal: true,
        scope: this,
        fn: function(button){
          if(button === "yes"){
            Ext.Ajax.request({
              url: "/sa/managedobject/actions/group_edit/",
              method: "POST",
              scope: me,
              jsonData: values,
              success: function(){
                NOC.info(__("Records has been updated"));
                me.getView().setHistoryHash();
                me.reloadSelectionGrids();
                me.toMain();
              },
              failure: function(){
                NOC.error(__("Failed"));
              },
            });
          }
        },
      });
    } else{
      me.toMain();
    }
  },
  onNewRecord: function(){
    this.newRecord();
  },
  onCloneRecord: function(){
    var view = this.getView(),
      parentController = view.up('[itemId=sa-managedobject]').getController(),
      formPanel = this.getView().down('[itemId=managedobject-form-panel]');
    parentController.setFormTitle(__("Clone") + " {0}", {id: "CLONE"});
    parentController.displayButtons(["closeBtn", "saveBtn", "resetBtn"]);
    formPanel.getForm().setValues({bi_id: null});
    formPanel.recordId = undefined;
    Ext.Array.each(view.query('[itemId$=-inline]'), function(grid){return grid.getStore().cloneData()});
  },
  onDeleteRecord: function(){
    var me = this;
    Ext.Msg.show({
      title: __("Delete record?"),
      msg: __("Do you wish to delete record? This operation cannot be undone!"),
      buttons: Ext.Msg.YESNO,
      icon: Ext.window.MessageBox.QUESTION,
      modal: true,
      fn: function(button){
        if(button == "yes")
          me.deleteRecord();
      },
    });
  },
  onResetRecord: function(){
    this.getView().up('[itemId=sa-managedobject]').getController().clearForm(this.getView().form);
    this.getView().up('[itemId=sa-managedobject]').getController().resetInlineStore(this.getView());
  },
  onConfig: function(){
    this.itemPreview('sa-config');
  },
  onConfDB: function(){
    this.itemPreview('sa-confdb');
  },
  onCard: function(){
    var formPanel = this.getView().down('[itemId=managedobject-form-panel]');
    if(formPanel.recordId){
      window.open(
        "/api/card/view/managedobject/" + formPanel.recordId + "/",
      );
    }
  },
  onDashboard: function(){
    var formPanel = this.getView().down('[itemId=managedobject-form-panel]');
    if(formPanel.recordId){
      window.open(
        "/ui/grafana/dashboard/script/noc.js?dashboard=mo&id=" + formPanel.recordId,
      );
    }
  },
  onConsole: function(){
    this.itemPreview('sa-console');
  },
  onScripts: function(){
    this.itemPreview('sa-script');
  },
  onInterfaces: function(){
    this.itemPreview('sa-interface_count');
  },
  onSensors: function(){
    this.itemPreview('sa-sensors');
  },
  onCPE: function(){},
  onLinks: function(){
    this.itemPreview('sa-link_count');
  },
  onDiscovery: function(){
    this.itemPreview('sa-discovery');
  },
  onAlarm: function(){
    this.itemPreview('sa-alarms');
  },
  onMaintenance: function(){},
  onInventory: function(){
    this.itemPreview('sa-inventory');
  },
  onInteractions: function(){
    this.itemPreview('sa-interactions');
  },
  onValidationSettings: function(){},
  onCaps: function(){},
  onHelpOpener: function(){},
  newRecord: function(defaults){
    var defaultValues = {},
      view = this.getView(),
      formPanel = this.getView().down('[itemId=managedobject-form-panel]'),
      parentController = view.up('[itemId=sa-managedobject]').getController(),
      fieldsWithDefaultValue = Ext.Array.filter(Ext.create("NOC.sa.managedobject.Model").fields,
                                                function(field){return !Ext.isEmpty(field.defaultValue)});

    Ext.Array.each(fieldsWithDefaultValue, function(field){
      defaultValues[field.name] = field.defaultValue;
    });
    parentController.setFormTitle(__("Create") + " {0}", {id: "NEW"});
    parentController.resetInlineStore(formPanel, defaults);
    parentController.displayButtons(["closeBtn", "saveBtn", "resetBtn"]);
    formPanel.recordId = undefined;
    this.getView().up('[itemId=sa-managedobject]').getController().clearForm(formPanel.getForm());
    formPanel.getForm().setValues(defaultValues);
  },
  saveRecord: function(data){
    var me = this, record,
      view = this.getView(),
      formPanel = view.down('[itemId=managedobject-form-panel]'),
      cust_field_model = view.up('[itemId=sa-managedobject]').noc.cust_model_fields || [];

    NOC.sa.managedobject.Model.addFields(cust_field_model.map(function(field){
      if(field.type === 'date'){field.type = "string"}
      return field;
    }));
    record = NOC.sa.managedobject.Model.create(data);

    record.self.setProxy({type: "managedobject"});
    record.getProxy().getWriter().setWriteAllFields(true);
    if(!record.validate().isValid()){
      // @todo: Error report
      NOC.error(__("Invalid data!"));
      return;
    }
    record.set("id", formPanel.recordId);
    if(formPanel.recordId){
      record.phantom = false;
      record.proxy.url += record.id + "/";
    }

    this.getView().mask(__("Saving ..."));
    this.getView().saveInlines(record.id,
                               Ext.Array.map(this.getView().query('[itemId$=-inline]'), function(grid){return grid.getStore()}));
    Ext.Object.each(data, function(key, value){if(!Ext.isEmpty(value)) record.set(key, value)});
    record.save({
      success: function(record, operation){
        me.getView().unmask();
        me.getView().setHistoryHash();
        me.reloadSelectionGrids();
        me.toMain();
        NOC.msg.complete(__("Saved"));
      },
      failure: function(record, operation){
        var message = __("Error saving record");
        me.getView().unmask();
        if(operation && operation.error && operation.error.response){
          if(operation.error.status !== 500 && operation.error.response.responseText){
            var response = Ext.decode(operation.error.response.responseText);
            if(response && response.message){
              message = response.message;
            }
          }
          if(operation.error.status === 500){
            message = __("Internal Error");
          }
        }
        NOC.error(message);
      },
    });
  },
  deleteRecord: function(){
    var formPanel = this.getView().down('[itemId=managedobject-form-panel]'),
      record = Ext.create("NOC.sa.managedobject.Model");

    record.self.setProxy({type: "managedobject"});
    if(formPanel.recordId){
      this.getView().mask(__("Deleting ..."));
      Ext.Ajax.request({
        url: "/sa/managedobject/" + formPanel.recordId + "/",
        method: "DELETE",
        scope: this,
        success: function(response){
          var basketStore = this.getView().up('[itemId=sa-managedobject]').down('[reference=saManagedobjectSelectedGrid1]').getStore();
          basketStore.remove(this.getView().down('[itemId=managedobject-form-panel]').currentRecord)
          this.reloadSelectionGrids();
          this.toMain();
          this.getView().unmask();
        },
        failure: function(response){
          var message;
          try{
            message = Ext.decode(response.responseText).message;
          } catch(err){
            message = "Internal error";
          }
          NOC.error(message);
          this.unmask();
        },
      });
    }
  },
  reloadSelectionGrids: function(){
    var parentController = this.getView().up('[itemId=sa-managedobject]').getController();
    parentController.reloadSelectionGrids();
  },
  gotoItem: function(itemName){
    var mainView = this.getView().up('[itemId=sa-managedobject]');
    mainView.setActiveItem(itemName);
    mainView.setHistoryHash();
  },
  itemPreview: function(itemName){
    var mainView = this.getView(),
      backItem = mainView.down('[itemId=managedobject-form-panel]'),
      activeItem = mainView.setActiveItem(itemName);
    if(activeItem !== false){
      activeItem.app = mainView.up('[itemId=sa-managedobject]');
      activeItem.preview(backItem.currentRecord, backItem);
    }
  },
  addTooltip: function(element){
    if(element.tooltip){
      Ext.create('Ext.tip.ToolTip', {
        target: element.getEl(),
        html: element.tooltip,
      });
    }
  },
  onChangeSNMP_SecurityLevel: function(field, value){
    this.getView().down('[name=snmp_ro]').setReadOnly(!["Community"].includes(value));
    this.getView().down('[name=snmp_rw]').setReadOnly(!["Community"].includes(value));
    this.getView().down('[name=snmp_username]').setReadOnly(!["noAuthNoPriv", "authNoPriv", "authPriv"].includes(value));
    this.getView().down('[name=snmp_ctx_name]').setReadOnly(!["noAuthNoPriv", "authNoPriv", "authPriv"].includes(value));
    this.getView().down('[itemId=snmp_auth_proto]').setHidden(["Community", "noAuthNoPriv"].includes(value));
    this.getView().down('[name=snmp_auth_key]').setHidden(["Community", "noAuthNoPriv"].includes(value));
    this.getView().down('[itemId=snmp_priv_proto]').setHidden(["Community", "noAuthNoPriv", "authNoPriv"].includes(value));
    this.getView().down('[name=snmp_priv_key]').setHidden(["Community", "noAuthNoPriv", "authNoPriv"].includes(value));
  },
  // Workaround labelField
  onChange: Ext.emptyFn,
});