.PHONY: test-flask test-integration

TAG="\n\n\033[0;32m\#\#\# "
END=" \#\#\# \033[0m\n"

test:
	@echo $(TAG)Running pylint$(END)
	pylint **/*.py
	@echo $(TAG)Running tests$(END)
	PYTHONPATH=. py.test -s ./tests/*_tests.py

run:
	python app.py