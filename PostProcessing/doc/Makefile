# Makefile to build Sphinx documentation in `build' subdirectory
# Run `make' to compile the documentation in HTML and LaTeX (PDF) format


# Variables

# subdirectory with Sphinx Makefile
SPHINXSRCDIR = src


# Make Targets

.PHONY: html

all: html latex

html:
	$(MAKE) -C $(SPHINXSRCDIR) html && rm -rf html && cp -R "$(SPHINXSRCDIR)/_build/html" .

latex:
	$(MAKE) -C $(SPHINXSRCDIR) latexpdf && rm -rf latex && mkdir latex && cp -R "$(SPHINXSRCDIR)/_build/latex/karma.pdf" latex/

clean:
	$(MAKE) -C $(SPHINXSRCDIR) clean && rm -rf html latex

forceclean:
	rm -rf src/_build
