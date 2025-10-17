//---------------------------------------------------------------------
// cm.interfacevalidationpolicy application
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.cm.interfacevalidationpolicy.Application");

Ext.define("NOC.cm.interfacevalidationpolicy.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.cm.interfacevalidationpolicy.Model",
    "NOC.cm.confdbquery.LookupField",
    "NOC.fm.alarmclass.LookupField",
    "NOC.core.ListFormField",
    "Ext.ux.form.GridField",
  ],
  model: "NOC.cm.interfacevalidationpolicy.Model",
  search: true,

  initComponent: function(){
    var me = this;
    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          flex: 1,
        },
      ],

      fields: [
        {
          name: "name",
          xtype: "textfield",
          fieldLabel: __("Name"),
          allowBlank: false,
          uiStyle: "medium",
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          allowBlank: true,
        },
        {
          name: "filter_query",
          xtype: "cm.confdbquery.LookupField",
          fieldLabel: __("Filter Query"),
          query: {
            allow_interface_filter: true,
          },
          allowBlank: true,
        },
        {
          name: "rules",
          xtype: "listform",
          fieldLabel: __("Rules"),
          items: [
            {
              name: "query",
              xtype: "cm.confdbquery.LookupField",
              fieldLabel: __("Query"),
              query: {
                allow_interface_validation: true,
              },
              listeners: {
                scope: me,
                select: me.onSelectQuery,
              },
            },
            {
              name: "query_params",
              xtype: "gridfield",
              fieldLabel: __("Query Parameters"),
              columns: [
                {
                  dataIndex: "name",
                  text: __("Name"),
                  width: 150,
                },
                {
                  dataIndex: "type",
                  text: __("Type"),
                  width: 70,
                },
                {
                  dataIndex: "value",
                  text: __("Value"),
                  editor: "textfield",
                  width: 200,
                },
                {
                  dataIndex: "default",
                  text: __("Default"),
                  width: 100,
                },
                {
                  dataIndex: "description",
                  text: __("Description"),
                  flex: 1,
                },
              ],
            },
            {
              name: "filter_query",
              xtype: "cm.confdbquery.LookupField",
              fieldLabel: __("Filter Query"),
              allowBlank: true,
              query: {
                allow_interface_filter: true,
              },
            },
            {
              name: "is_active",
              xtype: "checkbox",
              boxLabel: __("Active"),
            },
            {
              name: "error_code",
              xtype: "textfield",
              fieldLabel: __("Code"),
              allowBlank: true,
            },
            {
              name: "error_text_template",
              xtype: "textfield",
              fieldLabel: __("Error template"),
              placeHolder: "{{error}}",
              allowBlank: true,
              uiStyle: "extra",
            },
            {
              name: "alarm_class",
              xtype: "fm.alarmclass.LookupField",
              fieldLabel: __("Alarm Class"),
              allowBlank: true,
            },
            {
              name: "is_fatal",
              xtype: "checkbox",
              boxLabel: __("Fatal"),
            },
          ],
        },
      ],
    });
    me.callParent();
  },
  //
  onSelectQuery: function(field, record){
    var me = this;
    Ext.Ajax.request({
      url: "/cm/confdbquery/" + record.get("id") + "/",
      scope: me,
      success: function(response){
        var data = Ext.decode(response.responseText);
        field.up().getForm().findField("query_params").setValue(data.params)
      },
    })
  },
});
