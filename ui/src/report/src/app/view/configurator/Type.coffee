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
			queryMode: 'local'
			displayField: 'name'
			valueField: 'id'
			store:
				fields: ['name', 'id']
				data: [
					{id: 'grid', name: 'Таблица'}
				]
		}
	]