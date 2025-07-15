//---------------------------------------------------------------------
// aaa.user application
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.aaa.user.Application");

Ext.define("NOC.aaa.user.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.PasswordField",
    "NOC.aaa.user.Model",
    "NOC.aaa.group.Permission",
  ],
  model: "NOC.aaa.user.Model",
  search: true,
  recordReload: true,
  initComponent: function(){
    var me = this;
    me.setPasswordBtn = Ext.create(
      {
        xtype: "button",
        itemId: "password-update",
        text: __("Set password"),
        margin: "0 0 0 5",
        scope: me,
        handler: me.updatePassword,
      },
    );
    Ext.apply(me, {
      columns: [
        {
          text: __("Username"),
          dataIndex: "username",
          width: 110,
        },
        {
          text: __("e-mail Address"),
          dataIndex: "email",
          width: 150,
        },
        {
          text: __("First Name"),
          dataIndex: "first_name",
          width: 100,
        },
        {
          text: __("Last Name"),
          dataIndex: "last_name",
          width: 100,
        },
        {
          text: __("Active"),
          dataIndex: "is_active",
          renderer: NOC.render.Bool,
          width: 50,
        },
        {
          text: __("Superuser"),
          dataIndex: "is_superuser",
          renderer: NOC.render.Bool,
          width: 50,
        },
        {
          text: __("Last Login"),
          dataIndex: "last_login",
          renderer: NOC.render.DateTime,
          flex: 1,
        },
      ],
      fields: [
        {
          name: "username",
          xtype: "textfield",
          fieldLabel: __("Username"),
          autoFocus: true,
          allowBlank: false,
          uiStyle: "large",
          validator: me.usernameValidator,
        },
        {
          name: "email",
          xtype: "textfield",
          fieldLabel: __("e-mail Address"),
          vtype: "email",
          allowBlank: true,
          uiStyle: "large",
        },
        {
          name: "first_name",
          xtype: "textfield",
          fieldLabel: __("First Name"),
          allowBlank: true,
          uiStyle: "large",
        },
        {
          name: "last_name",
          xtype: "textfield",
          fieldLabel: __("Last Name"),
          allowBlank: true,
          uiStyle: "large",
        },
        {
          name: "is_active",
          xtype: "checkboxfield",
          fieldLabel: __("Active"),
          allowBlank: false,
        },
        {
          name: "is_superuser",
          xtype: "checkboxfield",
          fieldLabel: __("Superuser status"),
          allowBlank: true,
        },
        {
          xtype: "fieldcontainer",
          itemId: "password",
          fieldLabel: __("Password"),
          layout: "hbox",
          items: [
            {
              layout: "vbox",
              border: false,
              items: [
                {
                  xtype: "password",
                  name: "password",
                  uiStyle: "medium",
                },
                {
                  xtype: "password",
                  name: "password1",
                  uiStyle: "medium",
                },
              ],
            },
            me.setPasswordBtn,
          ],
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
                      "__limit": 0,
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
          xtype: "fieldcontainer",
          fieldLabel: __("User Permissions"),
          allowBlank: true,
          items: [
            {
              name: "permissions",
              xtype: "noc.group.permission",
            },
          ],
        },
        {
          name: "last_login",
          xtype: "displayfield",
          fieldLabel: __("Last Login"),
          allowBlank: true,
          renderer: NOC.render.DateTime,
        },
        {
          name: "date_joined",
          xtype: "displayfield",
          fieldLabel: __("Date of joined"),
          allowBlank: true,
          renderer: NOC.render.DateTime,
        },
      ],
    });
    me.callParent();
  },
  filters: [
    {
      title: __("Active"),
      name: "is_active",
      ftype: "boolean",
    },
    {
      title: __("Superuser"),
      name: "is_superuser",
      ftype: "boolean",
    },
  ],
  updatePassword: function(){
    var me = this,
      errMsg = __("Password mismatch"),
      passwordFieldset = me.down("[itemId=password]"),
      passwdField = me.form.findField("password"),
      passwd1Field = me.form.findField("password1");
    if(passwdField.getValue() === passwd1Field.getValue() && passwdField.getValue().length){
      passwordFieldset.unsetActiveError();
      Ext.Ajax.request({
        url: "/aaa/user/" + me.currentRecord.id + "/password/",
        method: "POST",
        jsonData: {password: passwdField.getValue()},
        scope: me,
        success: function(response){
          var data = Ext.decode(response.responseText);
          if(data.status){
            NOC.info(data.result);
          }
        },
        failure: function(){
          NOC.error(__("Failed to set password"));
        },
      });
    } else if(!passwdField.getValue().length){
      errMsg = __("Password empty");
      passwdField.markInvalid(errMsg);
      passwd1Field.markInvalid(errMsg);
    } else{
      passwdField.markInvalid(errMsg);
      passwd1Field.markInvalid(errMsg);
    }
  },
  editRecord: function(record){
    var groupsField = this.down("[name=groups]"),
      searchGrid = groupsField.down("[reference=searchGrid]");
    this.setPasswordBtn.show();
    if(searchGrid){
      searchGrid.getSelectionModel().deselectAll();
    }
    groupsField.getStore().loadData(record.get("groups"));
    this.callParent([record]);
  },
  newRecord: function(defaults){
    var groupsField = this.down("[name=groups]"),
      searchGrid = groupsField.down("[reference=searchGrid]");
    this.setPasswordBtn.hide();
    if(searchGrid){
      searchGrid.getSelectionModel().deselectAll();
    }
    this.callParent([defaults]);
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
    Ext.Ajax.request({
      url: "/aaa/group/new_permissions/",
      method: "GET",
      scope: me,
      success: function(response){
        var me = this,
          data = Ext.decode(response.responseText).data;
        me.newRecord({permissions: data.permissions});
      },
      failure: function(){
        NOC.error(__("Failed to get data"));
      },
    });
  },
  onReset: function(){
    var me = this, msg = __("Reset");
    me.mask(msg);
    Ext.TaskManager.start({
      run: function(){
        me.down("[name=groups]").getStore().removeAll();
        me.form.findField("permissions").resetAllPermission();
        me.unmask(msg);
      },
      interval: 0,
      repeat: 1,
      scope: me,
    });
    me.callParent();
  },
  usernameValidator: function(value){
    var tn = value.match(/^[\w.@+-]+$/, ""),
      errMsg = __("Invalid username");
    return tn ? true : errMsg;
  },
});
