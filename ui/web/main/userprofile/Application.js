//---------------------------------------------------------------------
// main.userprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.userprofile.Application");

Ext.define("NOC.main.userprofile.Application", {
  extend: "NOC.core.Application",
  requires: [
    "NOC.main.timepattern.LookupField",
    "NOC.main.ref.unotificationmethod.LookupField",
    "NOC.main.ref.ulanguage.LookupField",
    "Ext.ux.form.GridField",
  ],
  layout: "fit",
  //
  initComponent: function(){
    this.usernameField = Ext.create("Ext.form.field.Display", {
      fieldLabel: __("Login"),
    });
    this.nameField = Ext.create("Ext.form.field.Display", {
      fieldLabel: __("Name"),
    });
    this.emailField = Ext.create("Ext.form.field.Display", {
      fieldLabel: __("Mail"),
    });
    this.languageField = Ext.create("NOC.main.ref.ulanguage.LookupField", {
      fieldLabel: __("Language"),
      allowBlank: false,
    });
    this.groupsField = Ext.create("Ext.form.field.Display", {
      fieldLabel: __("Groups"),
    });
    // Contacts grid
    this.contactsGrid = Ext.create({
      xtype: "gridfield",
      columns: [
        {
          text: __("Time Pattern"),
          dataIndex: "time_pattern",
          width: 150,
          renderer: NOC.render.Lookup("time_pattern"),
          editor: "main.timepattern.LookupField",
        },
        {
          text: __("Method"),
          dataIndex: "notification_method",
          width: 120,
          editor: "main.ref.unotificationmethod.LookupField",
        },
        {
          text: __("Params"),
          dataIndex: "params",
          flex: 1,
          editor: "textfield",
        },
      ],
      getValue: function(){
        var records = [];
        this.store.each(function(r){
          var d = {};
          Ext.each(this.fields, function(f){
            // ToDo change Ext.ux.form.GridField
            var field_name = f.name || f;
            d[field_name] = r.get(field_name);
          });
          records.push(d);
        });
        return records;
      },
    });
    Ext.apply(this, {
      items: [
        {
          xtype: "form",
          defaults: {
            padding: "0 0 0 4px",
          },
          items: [
            this.usernameField,
            this.groupsField,
            this.nameField,
            this.emailField,
            this.languageField,
            {
              xtype: "fieldset",
              title: __("Notification Contacts"),
              defaults: {
                padding: 4,
              },
              border: false,
              items: [
                this.contactsGrid,
              ],
            },
          ],
          dockedItems: [
            {
              xtype: "toolbar",
              dock: "top",
              items: [
                {
                  glyph: NOC.glyph.save,
                  text: __("Save"),
                  scope: this,
                  handler: this.onSave,
                },
              ],
            },
          ],
        },
      ],
    });
    this.callParent();
    this.loadData();
    this.setHistoryHash();
  },
  //
  loadData: function(){
    Ext.Ajax.request({
      url: "/main/userprofile/",
      method: "GET",
      scope: this,
      success: function(response){
        this.setData(Ext.decode(response.responseText));
      },
      failure: function(){
        NOC.msg.failed(__("Failed to load data"))
      },
    });
  },
  //
  setData: function(data){
    this.profileData = data;
    this.usernameField.setValue(data.username);
    this.nameField.setValue(data.name);
    this.emailField.setValue(data.email);
    this.languageField.setValue(data.preferred_language);
    this.groupsField.setRawValue((data.groups || []).join(", "));
    this.contactsGrid.setValue(data.contacts || []);
  },
  //
  onSave: function(){
    var data = {
      preferred_language: this.languageField.getValue(),
      contacts: this.contactsGrid.getValue(),
    };
    Ext.Ajax.request({
      url: "/main/userprofile/",
      method: "POST",
      scope: this,
      jsonData: data,
      success: function(){
        NOC.msg.complete(__("Profile saved"));
        if(this.profileData.preferred_language !== data.preferred_language){
          NOC.app.app.restartApplication(__("Changing language"));
        }
      },
      failure: function(){
        NOC.msg.failed(__("Failed to save"))
      },
    });
  },
});
