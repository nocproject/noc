###
	Мета-данные сущности.
###
Ext.define 'Report.view.configurator.Meta',
	extend: 'Ext.container.Container'
	xtype: 'configuratorMeta'
	
	defaults:
		width: 275
		labelWidth: 70
	
	items: [
		{
			itemId: 'name'
			xtype: 'textfield'
			fieldLabel: 'Имя'
		}
		{
			itemId: 'tags'
			xtype: 'textfield'
			fieldLabel: 'Теги'
		}
		{
			itemId: 'description'
			xtype: 'textarea'
			fieldLabel: 'Описание'
			height: 150
		}
	]