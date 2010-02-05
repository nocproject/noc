# Makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = ../../../../contrib/bin/sphinx-build
PAPER         =
TARGET        = ../../../../static/doc/en/ag/

# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d $(TARGET)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .

.PHONY: help clean html web pickle htmlhelp latex changes linkcheck

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  html      to make standalone HTML files"
	@echo "  pickle    to make pickle files"
	@echo "  json      to make JSON files"
	@echo "  htmlhelp  to make HTML files and a HTML help project"
	@echo "  latex     to make LaTeX files, you can set PAPER=a4 or PAPER=letter"
	@echo "  changes   to make an overview over all changed/added/deprecated items"
	@echo "  linkcheck to check all external links for integrity"

clean:
	-rm -rf $(TARGET)/*

html:
	mkdir -p $(TARGET)/html $(TARGET)/doctrees
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(TARGET)/html
	@echo
	@echo "Build finished. The HTML pages are in $(TARGET)/html."

pickle:
	mkdir -p $(TARGET)/pickle $(TARGET)/doctrees
	$(SPHINXBUILD) -b pickle $(ALLSPHINXOPTS) $(TARGET)/pickle
	@echo
	@echo "Build finished; now you can process the pickle files."

web: pickle

json:
	mkdir -p $(TARGET)/json $(TARGET)/doctrees
	$(SPHINXBUILD) -b json $(ALLSPHINXOPTS) $(TARGET)/json
	@echo
	@echo "Build finished; now you can process the JSON files."

htmlhelp:
	mkdir -p $(TARGET)/htmlhelp $(TARGET)/doctrees
	$(SPHINXBUILD) -b htmlhelp $(ALLSPHINXOPTS) $(TARGET)/htmlhelp
	@echo
	@echo "Build finished; now you can run HTML Help Workshop with the" \
	      ".hhp project file in $(TARGET)/htmlhelp."

latex:
	mkdir -p $(TARGET)/latex $(TARGET)/doctrees
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS) $(TARGET)/latex
	@echo
	@echo "Build finished; the LaTeX files are in $(TARGET)/latex."
	@echo "Run \`make all-pdf' or \`make all-ps' in that directory to" \
	      "run these through (pdf)latex."

changes:
	mkdir -p $(TARGET)/changes $(TARGET)/doctrees
	$(SPHINXBUILD) -b changes $(ALLSPHINXOPTS) $(TARGET)/changes
	@echo
	@echo "The overview file is in $(TARGET)/changes."

linkcheck:
	mkdir -p $(TARGET)/linkcheck $(TARGET)/doctrees
	$(SPHINXBUILD) -b linkcheck $(ALLSPHINXOPTS) $(TARGET)/linkcheck
	@echo
	@echo "Link check complete; look for any errors in the above output " \
	      "or in $(TARGET)/linkcheck/output.txt."
