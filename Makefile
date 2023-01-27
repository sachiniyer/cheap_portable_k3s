##
# Resume
#
# @file
# @version 0.1
-include .gpa
build:
	@echo "Making PDF"
	@pdflatex README.tex > /dev/null
	@pandoc -s README.tex -o README.md > /dev/null
clean:
	@echo "Cleaning files"
	@rm README.aux README.log README.out README.pdf README.md > /dev/null
clean-no-pdf:
	@echo "Cleaning files (except pdfs/mds)"
	@rm README.aux README.log README.out > /dev/null




# end
