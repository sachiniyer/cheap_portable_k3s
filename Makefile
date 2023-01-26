##
# Resume
#
# @file
# @version 0.1
-include .gpa
build:
	@echo "Making PDF"
	@pdflatex info.tex > /dev/null
	@pandoc info.tex -o info.md > /dev/null
clean:
	@echo "Cleaning files"
	@rm info.aux info.log info.out info.pdf info.md > /dev/null
clean-no-pdf:
	@echo "Cleaning files (except pdfs/mds)"
	@rm info.aux info.log info.out > /dev/null




# end
