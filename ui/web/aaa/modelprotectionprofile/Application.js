//---------------------------------------------------------------------
// aaa.group application
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.aaa.modelprotectionprofile.Application");

Ext.define("NOC.aaa.modelprotectionprofile.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.aaa.modelprotectionprofile.Model",
    "NOC.core.ComboBox",
  ],
  model: "NOC.aaa.modelprotectionprofile.Model",
  search: true,
  recordReload: true,
  maskElement: "el",
  initComponent: function(){
    var me = this;
    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
        },
        {
          text: __("Description"),
          dataIndex: "description",
        },
        {
          text: __("Model"),
          dataIndex: "model",
        },
      ],
      fields: [
        {
          name: "name",
          xtype: "textfield",
          fieldLabel: __("Name"),
          allowBlank: false,
          autoFocus: true,
          tabIndex: 10,
          uiStyle: "large",
        },
        {
          name: "model",
          xtype: "textfield",
          fieldLabel: __("Model"),
          allowBlank: false,
          tabIndex: 20,
          uiStyle: "large",
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          allowBlank: true,
          tabIndex: 30,
          uiStyle: "expand",
        },
        {
          xtype: "fieldcontainer",
          fieldLabel: __("Groups"),
          items: [
            {
              xtype: "multiselector",
              name: "groups",
              title: __("Selected Groups"),
              fieldName: "label",
              viewConfig: {
                deferEmptyText: false,
                emptyText: __("No group selected"),
              },

              search: {
                field: "label",
                store: {
                  proxy: {
                    url: "/aaa/group/lookup/",
                    type: "rest",
                    pageParam: "__page",
                    startParam: "__start",
                    limitParam: "__limit",
                    sortParam: "__sort",
                    extraParams: {
                      "__format": "ext",
                    },
                    reader: {
                      type: "json",
                      rootProperty: "data",
                      totalProperty: "total",
                      successProperty: "success",
                    },
                  },
                },
              },
            },
          ],
        },
        {
          name: "field_access",
          xtype: "gridfield",
          fieldLabel: __("Field Access"),
          columns: [
            {
              text: __("Name"),
              dataIndex: "name",
              width: 150,
              renderer: NOC.render.Lookup("name"),
              editor: {
                xclass: "NOC.core.ComboBox",
              },
            },
            {
              text: __("Access"),
              dataIndex: "permission",
              width: 150,
              editor: {
                xtype: "combobox",
                store: [
                  [0, __("Hidden")],
                  [1, __("Disabled")],
                  [2, __("Read-Only")],
                  [3, __("Editable")],
                ],
                queryMode: "local",
              },
              renderer: NOC.render.Lookup("permission"),
            },
          ],
        },
      ],
    });
    me.callParent();
  },
  editRecord: function(record){
    this.down("[name=groups]").getStore().loadData(record.get("groups"));
    this.down("[name=field_access]").grid.getColumns()[0].getEditor().getStore()
        .getProxy().setUrl("/aaa/modelprotectionprofile/" + record.get("model") + "/fields/lookup/");
    this.callParent([record]);
  },
  saveRecord: function(data){
    var groups = [],
      groupStore = this.down("[name=groups]").getStore();
    groupStore.each(function(record){
      groups.push("" + record.id);
    });
    Ext.merge(data, {groups: groups});
    this.callParent([data]);
  },
  onNewRecord: function(){
    var me = this;
    me.down("[name=groups]").getStore().removeAll();
    this.callParent();
  },
  onReset: function(){
    var me = this, msg = __("Reset");
    me.mask(msg);
    Ext.TaskManager.start({
      run: function(){
        me.down("[name=groups]").getStore().removeAll();
        // me.form.findField("permissions").resetAllPermission();
        me.unmask(msg);
      },
      interval: 0,
      repeat: 1,
      scope: me,
    });
    me.callParent();
  },

});
