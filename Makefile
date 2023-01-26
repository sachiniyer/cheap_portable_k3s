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
	@rm resume.aux resume.log resume.out resume.pdf > /dev/null
	@rm resume-gpa.aux resume-gpa.log resume-gpa.out resume-gpa.pdf resume-gpa.tex > /dev/null
clean-no-pdf:
	@echo "Cleaning files (except pdfs)"
	@rm resume.aux resume.log resume.out > /dev/null
	@rm resume-gpa.aux resume-gpa.log resume-gpa.out resume-gpa.tex > /dev/null




# end
