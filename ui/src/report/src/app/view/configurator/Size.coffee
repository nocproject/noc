###
	Размеры сущности.
###
Ext.define 'Report.view.configurator.Size',
	extend: 'Ext.container.Container'
	xtype: 'configuratorSize'
	
	defaults:
		xtype: 'combobox'
		queryMode: 'local'
		displayField: 'value'
		valueField: 'value'
		width: 275
		labelWidth: 70
		store:
			fields: ['value']
			data: [
				{value: 1}
				{value: 2}
				{value: 3}
				{value: 4}
			]
	
	items: [
		{
			itemId: 'width'
			fieldLabel: 'Ширина'
		}
		{
			itemId: 'height'
			fieldLabel: 'Высота'
		}
	]