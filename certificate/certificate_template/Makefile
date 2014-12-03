# Makefile for Certificate

# bashful package available @
# http://www.ctan.org/tex-archive/macros/latex/contrib/bashful

# pst-barcode package available @
# http://www.ctan.org/tex-archive/graphics/pstricks/contrib/pst-barcode

# target is not a real file
.PHONY: help certificate clean

# default help
help:
	@echo "current make version is: "$(MAKE_VERSION)
	@echo "Please use \`make <target>' where <target> is one of"
	@echo ""
	@echo "certificate	        Generate certificate."
	@echo "clean		clean all tmp and pdf files."
	@echo "help		Show this help."
	@echo ""

# certificate
participant_cert:	SLC2014Pcertificate.pdf

SLC2014Pcertificate.pdf: SLC2014Pcertificate.tex fossee-logo.png bashful.sty
	pdflatex -shell-escape SLC2014Pcertificate.tex

paper_cert:	SLC2014Acertificate.pdf

SLC2014Acertificate.pdf: SLC2014Acertificate.tex fossee-logo.png bashful.sty
	pdflatex -shell-escape SLC2014Acertificate.tex

workshop_cert:	SLC2014Wcertificate.pdf

SLC2014Wcertificate.pdf: SLC2014Wcertificate.tex fossee-logo.png bashful.sty
	pdflatex -shell-escape SLC2014Wcertificate.tex

clean:	
	@echo "removing all tmp+pdf files"
	-rm -rvf *.pdf *~ *.aux *.log *.vrb *.out *.toc *.nav *.snm
	-rm -rvf *.std* *.sh
