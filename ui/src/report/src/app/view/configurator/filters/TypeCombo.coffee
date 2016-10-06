###
	Комбо выбора типа фильтра.
###
Ext.define 'Report.view.configurator.filters.TypeCombo',
	extend: 'Ext.form.field.ComboBox'
	xtype: 'configuratorFiltersTypeCombo'
	
	allowBlank: false
	queryMode: 'local'
	displayField: 'name'
	valueField: 'name'
	
	store:
		fields: ['name']
		data: [
			{name: '= (равно)'                }
			{name: '!= (не равно)'            }
			{name: '> (больше)'               }
			{name: '< (меньше)'               }
			{name: '>= (больше или равно)'    }
			{name: '<= (меньше или равно)'    }
			{name: 'r (регулярное выражение)' }
			{name: 'p (взять из дашборда)'    }
		]