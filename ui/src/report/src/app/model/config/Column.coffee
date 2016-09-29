###
	Модель конфигурации колонок для источника данных виджета.
###
Ext.define 'Report.model.config.Column',
	extend: 'Ext.data.Model'

	fields: [
		{name: 'id',   type: 'string'}
		{name: 'type', type: 'string'}
		{name: 'name', type: 'string'}
		
		# Для использования в интерфейсах выбора
		{name: 'selected', type: 'boolean'}
	]