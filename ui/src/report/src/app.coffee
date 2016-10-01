Ext.application(
	extend: 'Ext.app.Application'
	name: 'Report'
	
	requires: [
		'Report.view.root.Main'
		'Report.model.MainDataTree'
	]
	
	controllers: [
		'Root'
		'Configurator'
		'Dashboard'
		'Library'
		'Widget'
	]
	
	mainView: 'Report.view.root.Main'
	
	launch: () ->
		@showLoader()
		@makeReport()
		
	privates:
		
		###
            Отображает прелоадер.
		###
		showLoader: () ->
			body = Ext.getBody()
	
			loader = Ext.create 'Ext.Img',
				floating: true,
				src: 'resources/img/SOVA.png',
				alt: 'SOVA logo'
				autoShow: true,
				shadow: false,
				x: body.getWidth() / 2 - 380,
				y: body.getHeight() / 2 - 88
			
			loader.animate {
				delay: 1000
				duration: 1200
				to:
					opacity: 0
			}
			
			setTimeout(
				() -> loader.destroy()
				2500
			)

		###
            Создает-инициализирует отчет.
		###
		makeReport: () ->
			@controllers.getAt(0).makeReport()
)