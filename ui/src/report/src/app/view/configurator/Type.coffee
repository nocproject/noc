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
			valueField: 'id'
			displayField: 'name'
			autoSelect: true
			store:
				fields: ['id', 'name']
				data: [
					{id: 'grid', name: 'Таблица'}
				]
		}
	]