###
	Универсальный виджет, тип которого определяется конфигурацией.
	Типы конструируемых тел для виджетов можно изучить в пакете
	Report.view.widget.type.<WIDGET>
###
Ext.define 'Report.view.widget.Main',
	extend: 'Ext.panel.Panel'
	xtype: 'widgetMain'
	
	requires: [
		'Report.view.widget.type.Abstract'
		'Report.view.widget.type.Grid'
		'Report.view.widget.Configurator'
		'Report.view.widget.Library'
	]
	
	layout: 'fit'
	
	tools: [
		{
			itemId: 'configure'
			type: 'gear'
		}
	]
	
	config:
		
		###
			@cfg {Report.model.config.Widget} model Модель-конфиг виджета.
		###
		model: null
	
		###
			@cfg {String} type Тип виджета.
		###
		type: ''
	
		###
			@cfg {Ext.data.Store} columns Колонки источника данных в виде стора с моделями.
		###
		columns: null
	
		###
			@private
			@cfg {Ext.data.Store} store Стор данных виджета.
		###
		store: null
	
	initComponent: () ->
		@callParent arguments
	
		@add {
			xtype: @getWidgetXtype(),
			store: @makeStore()
			columns: @columns
		}
			
	privates:
		
		###
			Определяет xtype тела виджета по типу виджета,
			указанному в конфигурации.
		###
		getWidgetXtype: () ->
			switch @getType()
				when 'grid' then 'widgetTypeGrid'
		
		###
			Создает стор данных виджета.
			@return {Ext.data.Store} Стор.
		###
		makeStore: () ->
			Ext.create 'Ext.data.Store',
				fields: @makeFields()
				proxy: 'memory'
		
		###
			Создает упрощенную модель данных (fields) для стора.
			@param {String[]} Массив строк имен полей.
		###
		makeFields: () ->
			fields = []
			
			@columns.each (column) ->
				fields.push column.getId()
				
			fields
		