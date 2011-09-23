//---------------------------------------------------------------------
// {{module}}.{{app}} Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.{{module}}.{{app}}.Model");

Ext.define("NOC.{{module}}.{{app}}.Model", {
    extend: "Ext.data.Model",
    rest_url: "/{{module}}/{{app}}/",

    fields: [
        {
            name: "id",
            type: "string"
        },

        {% for f in fields %}
        {
            name: "{{f.name}}",
            {% if f.type == "CharField" %}
            type: "string",
            {% if f.default %}
            defaultValue: "{{f.default}}"
            {% endif %}
            {% endif %}
            {% if f.type == "TextField" %}
            type: "string",
            {% if f.default %}
            defaultValue: "{{f.default}}"
            {% endif %}
            {% endif %}
            {% if f.type == "IntegerField" %}
            type: "int",
            {% if f.default %}
            defaultValue: {{f.default}}
            {% endif %}
            {% endif %}
            {% if f.type == "BooleanField" %}
            type: "boolean",
            {% if f.default != None %}
            defaultValue: {% if f.default %}true{% else %}false{% endif %}
            {% endif %}
            {% endif %}
        }{% if not forloop.last %},{% endif %}
        {% endfor %}
    ]
});
