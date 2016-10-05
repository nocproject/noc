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
            Модель сущности, которую конфигурируем.
            Может отсутствовать если создается новая сущность.
        ###
		entityModel: null
	
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
	
	defaults:
		height: '100%'
		border: 1
		padding: 10
	
	items: [
		{
			xtype: 'container'
			layout: 'vbox'
			flex: 1
			cls: 'configurator-main-delimiter-border'
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
			cls: 'configurator-main-delimiter-border'
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
	
		model = @getEntityModel()
		
		if model
			@setTitle model.get 'name'
			
			###
                Оповещает о необходимости синхронизировать модель сущности и модель конфигуратора.
                @param {'Report.view.configurator.Main'} this Конфигуратор.
                @param {Ext.data.Model} model Модель сущности.
			###
			@fireEvent 'syncModels', @, model
		else
			@setTitle 'Новый'