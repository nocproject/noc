###
	Окно конфигуратора.
###
Ext.define 'Report.view.configurator.Main',
	extend: 'Report.view.ui.PopUpWindow'
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
            Ожидается что сущность имеет метод getModel.
            Может отсутствовать при создании новой сущности.
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
		
		###
            @cfg {Boolean} enableWellspringCombo
            Указывает на необходимость разблокировки списка источников данных.
        ###
		enableWellspringCombo: false
	
	
	###
        Модель конфигурируемой сущности.
        @property {Ext.data.Model} entityModel
	###
	entityModel: null
	
	
	defaults:
		height: '100%'
		border: 1
	
	items: [
		{
			xtype: 'container'
			layout: 'vbox'
			padding: 10
			flex: 1
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
			padding: 10
			flex: 1
		}
		{
			itemId: 'filters'
			xtype: 'configuratorFilters'
			flex: 2
		}
	]
	
	dockedItems: [
		{
			itemId: 'control'
			xtype: 'configuratorControl'
			dock: 'bottom'
		}
	]
	
	initComponent: () ->
		@callParent arguments
		
		if @getDisplayType() then @down('#type').show()
		if @getDisplaySize() then @down('#size').show()
		if @getEnableWellspringCombo() then @down('#wellspring').enableCombo()
	
		@entityModel = @getTargetEntity()?.getModel()
		
		@setTitle (@entityModel?.get 'name') or 'Новый'
		
		# TODO