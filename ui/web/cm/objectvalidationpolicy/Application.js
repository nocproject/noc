//---------------------------------------------------------------------
// cm.objectvalidationpolicy application
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.cm.objectvalidationpolicy.Application");

Ext.define("NOC.cm.objectvalidationpolicy.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.cm.objectvalidationpolicy.Model",
    "NOC.cm.confdbquery.LookupField",
    "NOC.fm.alarmclass.LookupField",
    "NOC.core.ListFormField",
    "Ext.ux.form.GridField",
  ],
  model: "NOC.cm.objectvalidationpolicy.Model",
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
          labelAlign: "top",
          allowBlank: false,
          uiStyle: "large",
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          labelAlign: "top",
          allowBlank: true,
        },
        {
          name: "filter_query",
          xtype: "cm.confdbquery.LookupField",
          fieldLabel: __("Filter Query"),
          labelAlign: "top",
          query: {
            allow_object_filter: true,
          },
          allowBlank: true,
          uiStyle: "large",
        },
        {
          name: "rules",
          xtype: "listform",
          fieldLabel: __("Rules"),
          labelAlign: "top",
          items: [
            {
              name: "query",
              xtype: "cm.confdbquery.LookupField",
              fieldLabel: __("Query"),
              query: {
                allow_object_validation: true,
              },
              listeners: {
                scope: me,
                select: me.onSelectQuery,
              },
              uiStyle: "large",
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
                allow_object_filter: true,
              },
              uiStyle: "large",
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
              uiStyle: "large",
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
        var data = Ext.decode(response.responseText),
          queryParamsField = field.up().getForm().findField("query_params"),
          rulesForm = field.up().up(),
          scrollPos = rulesForm.scroll;
        queryParamsField.setValue(data.params);
        rulesForm.scrollTo(scrollPos.x, scrollPos.y);
      },
    })
  },
});
