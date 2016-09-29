###
	Окно конфигуратора.
###
Ext.define 'Report.view.configurator.Main',
	extend: 'Ext.window.Window'
	xtype: 'configuratorMain'
	
	requires: [
		'Report.view.configurator.filters.Main'
		'Report.view.configurator.Control'
		'Report.view.configurator.Meta'
		'Report.view.configurator.Size'
		'Report.view.configurator.Type'
		'Report.view.configurator.Wellspring'
	]
	
	width: 1200
	height: 500
	layout: 'hbox'
	autoShow: true
	
	config:
	
		###
            Целевая сущность, которую будем конфигурировать.
            Ожидается что сущность имеет метод getStore.
        ###
		targetEntity: null
	
		###
			@cfg {Boolean} displayType
			Указывает на необходимость отображать выбор типа сущности.
		###
		displayType: false
		
		###
			@cfg {Boolean} displaySize
			Указывает на необходимость отображать настройки размера сущности.
		###
		displaySize: false
	
	items: [
		{
			xtype: 'container'
			layout: 'vbox'
			items: [
				{
					itemId: 'type'
					xtype: 'configuratorType'
					hidden: true
				}
				{
					itemId: 'meta'
					xtype: 'configuratorMeta'
				}
				{
					itemId: 'size'
					xtype: 'configuratorSize'
					hidden: true
				}
			]
		}
		{
			itemId: 'wellspring'
			xtype: 'configuratorWellspring'
		}
		{
			itemId: 'filters'
			xtype: 'configuratorFilters'
		}
	]
	
	initComponent: () ->
		@callParent arguments
		
		@mask()
		
		if @getDisplayType() then @down('#type').show()
		if @getDisplaySize() then @down('#size').show()
	
		@setEntityStore @getTargetEntity().getModel()
		
		# TODO