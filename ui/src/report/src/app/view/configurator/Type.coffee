###
	Тип виджета.
###
Ext.define 'Report.view.configurator.Type',
	extend: 'Ext.container.Container'
	xtype: 'configuratorType'
	
	items: [
		{
			itemId: 'combo'
			xtype: 'combobox'
			fieldLabel: 'Тип'
			width: 275
			labelWidth: 70
			queryMode: 'local'
			displayField: 'name'
			valueField: 'id'
			autoSelect: true
			store:
				fields: ['name', 'id']
				data: [
					{id: 'grid', name: 'Таблица'}
				]
		}
	]