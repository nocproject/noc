//---------------------------------------------------------------------
// {{module}}.{{app}} application
//---------------------------------------------------------------------
// Copyright (C) 2007-{{year}} The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.{{module}}.{{app}}.Application");

Ext.define("NOC.{{module}}.{{app}}.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        {%for r in requires%}"{{r}}"{% if forloop.last %}{%else%},
        {%endif%}{%endfor%}
    ],
    
    model: "NOC.{{module}}.{{app}}.Model",
    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                /*
                {
                    text: "Name",
                    dataIndex: "name"
                }*/
            ],

            fields: {{js_form_fields|safe}}
        });
        me.callParent();
    }
});
