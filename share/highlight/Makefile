##----------------------------------------------------------------------
## Generate JS highlight syntax
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

contrib_languages = diff
noc_languages = bind rpsl json text

languages = $(contrib_languages) $(noc_languages)

langfiles = $(addprefix ../../static/js/highlight/, $(addsuffix .js, $(languages)))

.PHONY: all lang

lang: $(langfiles)

../../static/js/highlight/%.js: %.lang
	./sh2js.sh $< $@

