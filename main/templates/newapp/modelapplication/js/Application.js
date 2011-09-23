//---------------------------------------------------------------------
// {{module}}.{{app}} application
//---------------------------------------------------------------------
// Copyright (C) 2007-{{year}} The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.{{module}}.{{app}}.Application");

Ext.define("NOC.{{module}}.{{app}}.Application", {
    extend: "NOC.core.ModelApplication",
    uses: ["NOC.{{module}}.{{app}}.Model"],
    
    model: "NOC.{{module}}.{{app}}.Model",
    
    columns: [
        /*
        {
            text: "Name",
            dataIndex: "name"
        }*/
    ],
    
    fields: [
        {% for f in fields %}
        {
            name: "{{f.name}}",
            {% if f.type == "CharField" %}
            xtype: "textfield",
            fieldLabel: "{{f.label}}",
            allowBlank: {% if f.null %}true{% else %}false{% endif %}
            {% endif %}
            {% if f.type == "TextField" %}
            xtype: "textfield",
            fieldLabel: "{{f.label}}",
            allowBlank: {% if f.null %}true{% else %}false{% endif %}
            {% endif %}
            {% if f.type == "IntegerField" %}
            xtype: "numberfield",
            fieldLabel: "{{f.label}}",
            allowBlank: {% if f.null %}true{% else %}false{% endif %}
            {% endif %}
            {% if f.type == "BooleanField" %}
            xtype: "checkboxfield",
            boxLabel: "{{f.label}}"
            {% endif %}
        }{% if not forloop.last %},{% endif %}
        {% endfor %}
    ]
});
