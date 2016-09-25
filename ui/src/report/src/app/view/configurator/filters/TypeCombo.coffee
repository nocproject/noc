###
    Комбо выбора типа фильтра.
###
Ext.define 'Report.view.configurator.filters.TypeCombo',
	extend: 'Ext.form.field.ComboBox'
	xtype: 'configuratorFiltersTypeCombo'
	
	allowBlank: false
	queryMode: 'local'
	displayField: 'title'
	valueField: 'type'
	
	store:
		fields: ['type', 'title']
		data: [
			{type: 'eq',  title: '='      }
			{type: 'gt',  title: '>'      }
			{type: 'gte', title: '> или ='}
			{type: 'lt',  title: '<'      }
			{type: 'lte', title: '< или ='}
			{type: 'btw', title: 'между'  }
		]