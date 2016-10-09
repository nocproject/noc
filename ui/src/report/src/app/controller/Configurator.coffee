###
	Управление логикой конфигуратора.
###
Ext.define 'Report.controller.Configurator',
	extend: 'Ext.app.Controller'
	id: 'configurator'
	
	requires: [
		'Report.model.configurator.Model'
	]
	
	listen:
		component:
			'configuratorMain':
				syncModels: 'syncModels'
			'configuratorMain configuratorControl #save':
				click: 'saveData'
	
	###
        Синхронизация моделей сущности и конфигуратора.
	###
	syncModels: (configurator, model) ->
		get = model.get.bind model
		set = @getValueSetter configurator
		
		set '#type #combo',       get 'type'
		set '#meta #name',        get 'name'
		set '#meta #tags',        get 'tags'
		set '#meta #description', get 'description'
		set '#size #width',       get 'width'
		set '#size #height',      get 'height'
		set '#wellspring #combo', get 'wellspring'
		set '#wellspring #grid',  get 'columns'
		set '#filters #grid',     get 'filters'
				
	###
        Сохраняет введенные данные.
        @param {Ext.button.Button} button Кнопка сохранения.
	###
	saveData: (button) ->
		configurator = button.up('configuratorMain')
		entityModel = configurator.getEntityModel()
		entityType = configurator.getEntityType()
		model = Ext.create 'Report.model.configurator.Model'
		get = @getValueGetter configurator
		
		model.set {
			type:        get '#type #combo'
			name:        get '#meta #name'
			tags:        get '#meta #tags'
			description: get '#meta #description'
			width:       get '#size #width'
			height:      get '#size #height'
			wellspring:  get '#wellspring #combo'
			columns:     get '#wellspring #grid'
			filters:     get '#filters #grid'
		}
			
		###
            Оповещает о начале сохранения данных конфигуратора.
            @param {Report.controller.Configurator} this Конфигуратор.
            @param {Report.model.configurator.Model} model Модель конфигуратора.
            @param {Ext.data.Model/Null} entityModel Модель сущности, которую конфигурируем, если есть.
            @param {String} entityType Тип сущности в виде произвольной строки.
        ###
		@fireEvent 'startSave', @, model, entityModel, entityType
		
		configurator.hide()
		
	privates:
		
		###
            Конструирует геттер, который принимает селектор
            и возвращает значение поля. Если полем является компонент,
            не являющийся полем - возвращается массив данных стора компонента в виде объетов.
            @param {Ext.Component} component Компонент.
            @return {Mixed} Значение.
		###
		getValueGetter: (component) -> (selector) =>
			target = component.down(selector)
			
			if target instanceof Ext.form.field.Base
				target.getValue()
			else
				data = target.getStore().getData()
				
				data.items.map (value) -> value.getData()
	
		###
			Конструирует сеттер, который принимает селектор и значение
			и устанавливает значение в поле конфигуратора. Если полем является компонент,
			не являющийся полем - устанавливает данные в стор компонента в виде объетов.
			@param {Ext.Component} component Компонент.
			@return {Mixed} Значение.
		###
		getValueSetter: (component) -> (selector, value) =>
			target = component.down(selector)
			
			if target instanceof Ext.form.field.Base
				target.setValue value
			else if value
				store = target.getStore()
				items = value.getData().items
				valueData = items.map (value) -> value.getData()
				
				store.loadData valueData