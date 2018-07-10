.PHONY: test-flask test-integration

TAG="\n\n\033[0;32m\#\#\# "
END=" \#\#\# \033[0m\n"
export FLASK_TESTING=1

test:
	@echo $(TAG)Running tests$(END)
	PYTHONPATH=. py.test -s ./tests/*Tests.py