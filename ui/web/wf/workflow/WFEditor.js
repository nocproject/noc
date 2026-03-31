//---------------------------------------------------------------------
// Workflow editor, JointJS version
//---------------------------------------------------------------------
// Copyright (C) 2007-2026 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.wf.workflow.WFEditor");

Ext.define("NOC.wf.workflow.WFEditor", {
  extend: "NOC.core.ApplicationPanel",
  requires: [
    "Ext.ux.form.StringsField",
    "NOC.core.label.LabelField",
    "NOC.core.tagfield.Tagfield",
    "NOC.main.ref.modelid.LookupField",
  ],
  config: {
    scriptsLoaded: false,
  },
  mixins: {
    observable: "Ext.util.Observable",
  },
  constructor: function(config){
    this.mixins.observable.constructor.call(this, config);
    this.callParent();
  },
  updateScriptsLoaded: function(newValue){
    var me = this;
    me.fireEvent("scriptsLoaded", newValue);
  },
  initComponent: function(){
    var me = this;

    me.blankMenu = Ext.create("Ext.menu.Menu", {
      items: [
        {
          text: __("Add State"),
          glyph: NOC.glyph.plus,
          scope: me,
          handler: me.onAddState,
        },
      ],
    });
    me.menuPosition = {x: 0, y: 0};
    me.isInspectorDirty = false;
    me.currentSelection = {kind: "workflow", data: null};
    me.suspendSelectionSync = false;
    me.inspector = {
      xtype: "form",
      itemId: "inspector",
      flex: 1,
      scrollable: "vertical",
      bodyPadding: "10",
      defaults: {
        labelAlign: "top",
        width: "100%",
      },
      listeners: {
        scope: me,
        dirtychange: me.onInspectorDirty,
      },
      buttons: [
        {
          text: __("Submit"),
          disabled: true,
          formBind: true,
          scope: me,
          handler: me.onSubmitInspector,
        },
      ],
    };
    Ext.apply(me, {
      tbar: [
        me.getCloseButton(),
        "-",
        {
          xtype: "button",
          tooltip: __("Delete Workflow"),
          text: __("Delete"),
          glyph: NOC.glyph.remove,
          scope: me,
          handler: me.onDeleteClick,
        },
        "-",
        {
          xtype: "button",
          tooltip: __("Save Workflow"),
          text: __("Save"),
          glyph: NOC.glyph.save,
          scope: me,
          handler: me.onSaveClick,
        },
      ],
      layout: {
        type: "hbox",
        align: "stretch",
      },
      items: [
        {
          xtype: "container",
          itemId: "container",
          flex: 4,
        },
      ],
    });
    me.callParent();
  },
  afterRender: function(){
    var me = this;
    me.callParent();
    me.initMap();
  },
  beforeDestroy: function(){
    var me = this,
      module;
    if(me.containerDom){
      me.containerDom.removeEventListener("contextmenu", me.onNativeContextMenuBound || me.onNativeContextMenu);
    }
    if(me.editor){
      module = me.getEditorModule();
      if(module){
        if(me.onEditorSelectionChangeBound){
          me.editor.removeEventListener(module.WORKFLOW_SELECTION_CHANGE_EVENT, me.onEditorSelectionChangeBound);
        }
        if(me.onEditorContextMenuBound){
          me.editor.removeEventListener(module.WORKFLOW_CONTEXTMENU_EVENT, me.onEditorContextMenuBound);
        }
      }
      if(Ext.isFunction(me.editor.destroy)){
        me.editor.destroy();
      }
      me.editor = null;
    }
    me.callParent();
  },
  getEditorModule: function(){
    var module = window.map;
    if(!module || !module.WorkflowEditor){
      NOC.error(__("Workflow editor module is not loaded"));
      return null;
    }
    return module;
  },
  initMap: function(){
    var me = this,
      dom = me.getComponent("container").el.dom,
      module = me.getEditorModule();

    if(!module){
      return;
    }

    me.workflow = me.loadData({
      name: "New Workflow",
      description: "",
      is_active: true,
      allowed_models: [],
    }, "workflow");
    me.editor = new module.WorkflowEditor({
      mainContainer: dom,
      fitToPageOnLoad: true,
      gridSize: 20,
    });
    me.containerDom = dom;
    me.onNativeContextMenuBound = Ext.bind(me.onNativeContextMenu, me);
    me.onEditorSelectionChangeBound = function(event){
      me.onEditorSelectionChange(event.detail.selection);
    };
    me.onEditorContextMenuBound = function(event){
      me.onEditorContextMenu(event.detail);
    };
    me.editor.addEventListener(module.WORKFLOW_SELECTION_CHANGE_EVENT, me.onEditorSelectionChangeBound);
    me.editor.addEventListener(module.WORKFLOW_CONTEXTMENU_EVENT, me.onEditorContextMenuBound);
    dom.addEventListener("contextmenu", me.onNativeContextMenuBound);
    me.setScriptsLoaded(true);
  },
  preview: function(record){
    var me = this;
    if(record){
      me.configId = record.get("id");
      Ext.Ajax.request({
        url: "/wf/workflow/" + me.configId + "/config/",
        method: "GET",
        scope: me,
        success: function(response){
          me.draw(Ext.decode(response.responseText));
        },
        failure: function(){
          NOC.error(__("Failed to get data"));
        },
      });
    } else{
      me.configId = "000000000000000000000000";
      me.draw({
        id: me.configId,
        name: "New Workflow",
        description: "New Workflow diagram",
        is_active: true,
        allowed_models: [],
        states: [],
        transitions: [],
      });
    }
    me.callParent(arguments);
  },
  draw: function(data){
    var me = this;
    if(!me.editor){
      return;
    }
    me.editor.loadWorkflow(data);
    me.applySelection({
      kind: "workflow",
      data: me.workflow,
    });
  },
  onEditorSelectionChange: function(selection){
    var me = this;
    if(me.suspendSelectionSync){
      return;
    }
    if(me.isInspectorDirty){
      Ext.Msg.show({
        title: __("Unsaved data"),
        msg: __("You have unsaved changes in inspector. Save or cancel the changes."),
        buttons: Ext.Msg.YESNOCANCEL,
        icon: Ext.MessageBox.WARNING,
        modal: true,
        scope: me,
        fn: function(button){
          if(button === "yes"){
            if(!me.onSubmitInspector()){
              me.restoreEditorSelection();
            }
          }
          if(button === "no"){
            me.isInspectorDirty = false;
            me.applySelection(selection);
          }
          if(button === "cancel"){
            me.restoreEditorSelection();
          }
        },
      });
      return;
    }
    me.applySelection(selection);
  },
  onEditorContextMenu: function(detail){
    var me = this;
    if(detail.kind !== "blank"){
      return;
    }
    me.menuPosition = {x: detail.localX, y: detail.localY};
    me.blankMenu.showAt(detail.clientX, detail.clientY);
  },
  onNativeContextMenu: function(event){
    var me = this,
      localPoint,
      target,
      paper;
    if(!me.editor){
      return;
    }
    target = event.target;
    if(target && target.closest && target.closest("[model-id]")){
      return;
    }
    event.preventDefault();
    if(me.editor.clientToLocalPoint && Ext.isFunction(me.editor.clientToLocalPoint)){
      localPoint = me.editor.clientToLocalPoint(event.clientX, event.clientY);
    } else{
      paper = me.editor.paper;
      if(paper && Ext.isFunction(paper.clientToLocalPoint)){
        localPoint = paper.clientToLocalPoint({x: event.clientX, y: event.clientY});
      } else{
        localPoint = {x: event.offsetX || 0, y: event.offsetY || 0};
      }
    }
    me.menuPosition = {x: localPoint.x, y: localPoint.y};
    me.blankMenu.showAt(event.clientX, event.clientY);
  },
  restoreEditorSelection: function(){
    var me = this,
      selection = me.currentSelection;
    if(!me.editor){
      return;
    }
    me.suspendSelectionSync = true;
    try{
      if(!selection || selection.kind === "workflow"){
        me.editor.clearSelection();
      } else{
        me.editor.selectCell(selection.id);
      }
    } finally{
      me.suspendSelectionSync = false;
    }
  },
  applySelection: function(selection){
    var me = this,
      data;

    me.refreshWorkflowSnapshot();
    if(!selection || selection.kind === "workflow"){
      me.currentSelection = {
        kind: "workflow",
        data: Ext.clone(me.workflow),
      };
      me.showWorkflowInspector(me.workflow);
      return;
    }

    if(selection.kind === "state"){
      data = me.loadData(selection.data, "state");
      me.currentSelection = {
        kind: "state",
        id: selection.id,
        data: data,
      };
      me.showStateInspector(data);
      return;
    }

    data = me.loadData(selection.data, "transition");
    me.currentSelection = {
      kind: "transition",
      id: selection.id,
      data: data,
    };
    me.showTransitionInspector(data);
  },
  refreshWorkflowSnapshot: function(){
    var me = this,
      document;
    if(!me.editor){
      return null;
    }
    document = me.editor.toJSON();
    me.workflow = me.loadData(document, "workflow");
    return document;
  },
  clearInspector: function(){
    var me = this,
      inspector = me.getComponent("inspector");
    me.isInspectorDirty = false;
    if(inspector && Ext.isFunction(inspector.destroy)){
      inspector.destroy();
    }
  },
  showInspector: function(data, fields, title){
    var me = this, inspector,
      modelName = me.getModelName(data.type),
      record;

    if(!modelName){
      NOC.error(__("Unknown type: ") + data.type);
      return;
    }
    record = Ext.create(modelName);
    record.set(data);
    me.clearInspector();

    me.inspector.items = fields.map(function(field){
      if(Object.hasOwn(data, field.name)){
        field.value = data[field.name];
      }
      if(field.xtype === "fieldset"){
        field.items = field.items.map(function(item){
          if(Object.hasOwn(data, item.name)){
            item.value = data[item.name];
          }
          return item;
        });
      }
      return field;
    });
    me.inspector.record = record;
    me.inspector.title = title;
    inspector = Ext.create(me.inspector);
    me.add(inspector);
  },
  showWorkflowInspector: function(data){
    var me = this,
      fields = [
        {
          name: "name",
          xtype: "textfield",
          fieldLabel: __("Name"),
          allowBlank: false,
        },
        {
          name: "is_active",
          xtype: "checkbox",
          boxLabel: __("Active"),
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          allowBlank: true,
        },
        {
          name: "allowed_models",
          xtype: "core.tagfield",
          url: "/main/ref/modelid/lookup/",
          fieldLabel: __("Allowed models"),
          tooltip: __("Models allowed set workflow"),
        },
        {
          xtype: "fieldset",
          layout: "vbox",
          title: __("Integration"),
          defaults: {
            padding: 4,
            labelAlign: "top",
            disabled: true,
          },
          items: [
            {
              name: "remote_system",
              xtype: "main.remotesystem.LookupField",
              fieldLabel: __("Remote System"),
              allowBlank: true,
            },
            {
              name: "remote_id",
              xtype: "textfield",
              fieldLabel: __("Remote ID"),
              allowBlank: true,
            },
            {
              name: "bi_id",
              xtype: "displayfield",
              fieldLabel: __("BI ID"),
              allowBlank: true,
            },
          ],
        },
      ];
    me.showInspector(data, fields, __("Workflow Inspector"));
  },
  showStateInspector: function(data){
    var me = this,
      fields = [
        {
          name: "name",
          xtype: "textfield",
          fieldLabel: __("Name"),
          allowBlank: false,
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          allowBlank: true,
        },
        {
          name: "is_default",
          xtype: "checkbox",
          boxLabel: __("Default"),
        },
        {
          name: "is_productive",
          xtype: "checkbox",
          boxLabel: __("Productive"),
        },
        {
          name: "is_wiping",
          xtype: "checkbox",
          boxLabel: __("Wiping"),
        },
        {
          name: "update_last_seen",
          xtype: "checkbox",
          boxLabel: __("Update Last Seen"),
        },
        {
          name: "ttl",
          xtype: "numberfield",
          fieldLabel: __("TTL"),
          allowBlank: true,
          minValue: 0,
          emptyText: __("Not Limited"),
        },
        {
          name: "update_expired",
          xtype: "checkbox",
          boxLabel: __("Update Expiration"),
        },
        {
          name: "labels",
          xtype: "labelfield",
          fieldLabel: __("Labels"),
        },
        {
          name: "job_handler",
          xtype: "textfield",
          fieldLabel: __("Job Handler"),
        },
        {
          xtype: "fieldset",
          layout: "vbox",
          title: __("Integration"),
          defaults: {
            padding: 4,
            labelAlign: "top",
            disabled: true,
          },
          items: [
            {
              name: "remote_system",
              xtype: "main.remotesystem.LookupField",
              fieldLabel: __("Remote System"),
              allowBlank: true,
            },
            {
              name: "remote_id",
              xtype: "textfield",
              fieldLabel: __("Remote ID"),
              allowBlank: true,
            },
            {
              name: "bi_id",
              xtype: "displayfield",
              fieldLabel: __("BI ID"),
              allowBlank: true,
            },
          ],
        },
        {
          name: "on_enter_handlers",
          xtype: "stringsfield",
          fieldLabel: __("On Enter Handlers"),
          allowBlank: true,
        },
        {
          name: "on_leave_handlers",
          xtype: "stringsfield",
          fieldLabel: __("On Leave Handlers"),
          allowBlank: true,
        },
      ];
    me.showInspector(data, fields, __("State Inspector"));
  },
  showTransitionInspector: function(data){
    var me = this,
      fields = [
        {
          name: "label",
          xtype: "textfield",
          fieldLabel: __("Label"),
          allowBlank: false,
        },
        {
          name: "event",
          xtype: "textfield",
          fieldLabel: __("Event"),
          allowBlank: true,
        },
        {
          name: "is_active",
          xtype: "checkbox",
          boxLabel: __("Active"),
        },
        {
          name: "enable_manual",
          xtype: "checkbox",
          boxLabel: __("Enable Manual"),
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          allowBlank: true,
        },
        {
          xtype: "fieldset",
          layout: "vbox",
          title: __("Integration"),
          defaults: {
            padding: 4,
            labelAlign: "top",
            disabled: true,
          },
          items: [
            {
              name: "remote_system",
              xtype: "main.remotesystem.LookupField",
              fieldLabel: __("Remote System"),
              allowBlank: true,
            },
            {
              name: "remote_id",
              xtype: "textfield",
              fieldLabel: __("Remote ID"),
              allowBlank: true,
            },
            {
              name: "bi_id",
              xtype: "displayfield",
              fieldLabel: __("BI ID"),
              allowBlank: true,
            },
          ],
        },
        {
          name: "handlers",
          xtype: "stringsfield",
          fieldLabel: __("Handlers"),
          allowBlank: true,
        },
      ];
    me.showInspector(data, fields, __("Transition Inspector"));
  },
  onSubmitInspector: function(){
    var me = this,
      data,
      form = me.getComponent("inspector");
    if(!form || !form.isValid()){
      return false;
    }

    form.updateRecord(form.record);
    data = form.record.getData();
    me.isInspectorDirty = false;
    if(!me.editor || !me.currentSelection){
      return true;
    }

    switch(me.currentSelection.kind){
      case "state":
        me.editor.updateState(me.currentSelection.id, me.toPatch(data));
        break;
      case "transition":
        me.editor.updateTransition(me.currentSelection.id, me.toPatch(data));
        break;
      default:
        me.editor.updateWorkflowMeta(me.toPatch(data));
        break;
    }

    me.applySelection(me.editor.getSelection());
    return true;
  },
  toPatch: function(data){
    var patch = Ext.clone(data);
    delete patch.type;
    return patch;
  },
  onDeleteClick: function(){
    var me = this;
    Ext.Msg.show({
      title: __("Delete Workflow?"),
      msg: __("Do you wish to delete Workflow? This operation cannot be undone!"),
      buttons: Ext.Msg.YESNO,
      icon: Ext.window.MessageBox.QUESTION,
      modal: true,
      fn: function(button){
        if(button === "yes"){
          me.app.deleteRecord();
          me.onClose();
        }
      },
    });
  },
  onSaveClick: function(){
    var me = this;
    me.dirtyCheck(me.save);
  },
  save: function(){
    var me = this,
      ret;
    if(!me.configId){
      NOC.error(__("Create new diagram not implement"));
      return;
    }
    if(!me.editor){
      NOC.error(__("Workflow editor is not initialized"));
      return;
    }

    ret = me.sanitizeWorkflowForSave(me.editor.exportForSave());
    Ext.Ajax.request({
      url: "/wf/workflow/" + me.configId + "/config/",
      method: "POST",
      jsonData: ret,
      scope: me,
      success: function(){
        me.onClose();
        NOC.info(__("Config saved"));
      },
      failure: function(){
        NOC.error(__("Failed save data"));
      },
    });
  },
  sanitizeWorkflowForSave: function(data){
    var me = this,
      ret = Ext.clone(data);

    delete ret["uuid"];
    delete ret["bi_id"];
    delete ret["type"];
    delete ret["kind"];
    delete ret["id"];

    if(ret["allowed_models"] != null && ret["allowed_models"].length !== 0){
      ret["allowed_models"] = ret["allowed_models"].map(function(item){
        return Ext.isDefined(item.id) ? item.id : item;
      });
    }

    ret.states = (ret.states || []).map(function(item){
      return me.sanitizeStateForSave(item);
    });
    ret.transitions = (ret.transitions || []).map(function(item){
      return me.sanitizeTransitionForSave(item);
    });
    return ret;
  },
  sanitizeStateForSave: function(data){
    var ret = Ext.clone(data);
    if(ret["job_handler"] != null && ret["job_handler"].length === 0){
      ret["job_handler"] = null;
    }
    if(Object.hasOwn(ret, "remote_system") && ret["remote_system"] != null && ret["remote_system"].length === 0){
      delete ret["remote_system"];
    }
    if(Object.hasOwn(ret, "remote_id") && ret["remote_id"] != null && ret["remote_id"].length === 0){
      delete ret["remote_id"];
    }
    delete ret["bi_id"];
    delete ret["uuid"];
    delete ret["position"];
    delete ret["type"];
    delete ret["kind"];
    delete ret["update_ttl"];
    delete ret["workflow"];
    delete ret["workflow__label"];
    return ret;
  },
  sanitizeTransitionForSave: function(data){
    var ret = Ext.clone(data);
    if(Object.hasOwn(ret, "remote_system") && ret["remote_system"] != null && ret["remote_system"].length === 0){
      delete ret["remote_system"];
    }
    if(Object.hasOwn(ret, "remote_id") && ret["remote_id"] != null && ret["remote_id"].length === 0){
      delete ret["remote_id"];
    }
    delete ret["bi_id"];
    delete ret["uuid"];
    delete ret["remote_system__label"];
    delete ret["workflow__label"];
    delete ret["from_state__label"];
    delete ret["to_state__label"];
    delete ret["type"];
    delete ret["kind"];
    delete ret["sourceStateId"];
    delete ret["targetStateId"];
    return ret;
  },
  openBlankMenu: function(){
    return;
  },
  onAddState: function(){
    var me = this;
    if(!me.editor){
      return;
    }
    me.editor.addState(me.menuPosition, {
      name: "New State",
      on_enter_handlers: [],
      on_leave_handlers: [],
      job_handler: null,
      labels: [],
    });
    me.refreshWorkflowSnapshot();
  },
  loadData: function(data, type){
    var ret = {type: type};
    Ext.Object.each(data, function(key, value){
      if(["states", "transitions"].indexOf(key) === -1){
        ret[key] = value;
      }
    });
    return ret;
  },
  getModelName: function(type){
    switch(type){
      case "transition":
        return "NOC.wf.transition.Model";
      case "state":
        return "NOC.wf.state.Model";
      case "workflow":
        return "NOC.wf.workflow.Model";
      default:
        return null;
    }
  },
  onInspectorDirty: function(){
    var me = this;
    me.isInspectorDirty = true;
  },
  dirtyCheck: function(handler, args){
    var me = this;
    if(me.isInspectorDirty){
      Ext.Msg.show({
        title: __("Unsaved data"),
        msg: __("You have unsaved changes in inspector. Save or cancel the changes."),
        buttons: Ext.Msg.YESNOCANCEL,
        icon: Ext.MessageBox.WARNING,
        modal: true,
        scope: me,
        fn: function(button){
          if(button === "yes"){
            if(me.onSubmitInspector()){
              handler.call(me, args);
            }
          }
          if(button === "no"){
            me.isInspectorDirty = false;
            handler.call(me, args);
          }
        },
      });
    } else{
      handler.call(me, args);
    }
  },
  onClose: function(){
    var me = this;
    me.app.onClose();
  },
  changeStatenameInTransition: function(){
    return;
  },
});
