# Minimal makefile for Sphinx documentation
#
# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = docs

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile clean process-emails copy-images

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Custom clean target to clean the build directories
clean:
	@echo "Removing generated files..."
	@rm -rf $(BUILDDIR)/*

# New target to process emails
process-emails:
	@echo "Processing email files..."
	@python process_eml.py

# New target to copy images
copy-images:
	@echo "Copying images..."
	@mkdir -p $(BUILDDIR)/_images
	@cp -R $(SOURCEDIR)/_images/* $(BUILDDIR)/_images/

# Updated html target to process emails before building and copy images after
html: process-emails
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS)
	@echo "Moving built files to the root of $(BUILDDIR)..."
	@mv $(BUILDDIR)/html/* $(BUILDDIR)
	@echo "Removing now-empty html directory and doctrees..."
	@rm -rf $(BUILDDIR)/html
	@rm -rf $(BUILDDIR)/doctrees
	@$(MAKE) copy-images
	@echo "Build finished. The HTML pages are in $(BUILDDIR)."