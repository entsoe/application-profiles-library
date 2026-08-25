rdf-validate:
	ls -1 ../*/SHACL/* | xargs -n 10 riot --validate > rdf-validate.txt

sparql-validate: # parse .rq file with qparse, print only files with errors
	@echo > sparql-validate.txt
	@for f in shacl-sparql/*.rq; do \
	  err=`qparse --strict --query "$$f" 2>&1 >/dev/null`; \
	  if [ -n "$$err" ]; then echo "== $$f ==" >> sparql-validate.txt; echo "$$err" >> sparql-validate.txt; fi; \
	done

zip: # first remove, in case file locations have changed. The zip itself is in .gitignore
	rm -f entsoe-SHACL.zip
	zip -9 entsoe-SHACL.zip ../*/SHACL/* 
