# Makefile for Certificate

# bashful package available @
# http://www.ctan.org/tex-archive/macros/latex/contrib/bashful

# pst-barcode package available @
# http://www.ctan.org/tex-archive/graphics/pstricks/contrib/pst-barcode

# target is not a real file
.PHONY: help certificate clean

# following line is because on server texlive is not installed system-wide
#export PATH := /usr/local/texlive/2014/bin/x86_64-linux:$(PATH)

# default help
help:
	@echo "current make version is: "$(MAKE_VERSION)
	@echo "Please use \`make <target>' where <target> is one of"
	@echo ""
	@echo "participant_cert file_name=xyz       Generate certificate."
	@echo "clean                                clean all tmp and pdf files."
	@echo "help                                 Show this help."
	@echo ""

name = $(file_name)

# certificate
participant_cert: $(name).tex fossee-logo.png bashful.sty
	pdflatex -shell-escape $(name).tex

paper_cert:	$(name).tex fossee-logo.png bashful.sty
	pdflatex -shell-escape $(name).tex

workshop_cert:	$(name).tex fossee-logo.png bashful.sty
	pdflatex -shell-escape $(name).tex


clean:
	@echo "removing all tmp+pdf files"
	-rm -rvf $(name)*.pdf *~ $(name).aux $(name).log $(name).tex *.vrb *.out *.toc *.nav *.snm
	-rm -rvf *.std* *.sh
