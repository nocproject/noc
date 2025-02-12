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
    "NOC.core.ComboBox",
    "NOC.main.timepattern.LookupField",
    "NOC.main.ref.unotificationmethod.LookupField",
    "NOC.main.ref.ulanguage.LookupField",
    "Ext.ux.form.GridField",
  ],
  layout: "fit",
  //
  initComponent: function(){
    // Contacts grid
    this.contactsGrid = Ext.create({
      xtype: "gridfield",
      name: "contacts",
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
    this.items = [
      {
        xtype: "form",
        defaults: {
          padding: "0 0 0 4px",
          xtype: "displayfield",
        },
        items: [
          {
            fieldLabel: __("Login"),
            name: "username",
          },
          {
            fieldLabel: __("Groups"),
            name: "groups",
          },
          {
            fieldLabel: __("Name"),
            name: "name",
          },
          {
            fieldLabel: __("Mail"),
            name: "email",
          },
          {
            xtype: "core.combo",
            restUrl: "/main/ref/ulanguage/lookup/",
            fieldLabel: __("Language"),
            allowBlank: false,
            typeAhead: false,
            editable: false,
            uiStyle: "medium-combo",
            name: "preferred_language",
          },
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
    ];
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
        var data = Ext.decode(response.responseText);
        data.group = (data.groups || []).join(", ");
        this.down("form").getForm().setValues(data);
        // save for later restart if language changed
        this.preferred_language = data.preferred_language;
      },
      failure: function(){
        NOC.msg.failed(__("Failed to load data"))
      },
    });
  },
  //
  onSave: function(){
    var
      languageField = this.down("form field[name=preferred_language]"),
      data = {
        preferred_language: languageField.getValue(),
        contacts: this.contactsGrid.getValue(),
      };
    Ext.Ajax.request({
      url: "/main/userprofile/",
      method: "POST",
      scope: this,
      jsonData: data,
      success: function(){
        NOC.msg.complete(__("Profile saved"));
        if(this.preferred_language !== data.preferred_language){
          NOC.app.app.restartApplication(__("Changing language"));
        }
      },
      failure: function(response){
        var message = Ext.decode(response.responseText);
        NOC.msg.failed(message.errors || __("Failed to save"));
      },
    });
  },
});
