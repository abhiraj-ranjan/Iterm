.PHONY: check_programs run clean build

all : check_programs run

backend = "linux"


check_programs:
	@echo $(shell PATH=$(PATH) which python3)


venv/bin/activate: ../requirements.txt
	@echo "cleaning directory"
	@rm -rf __pycache__
	@rm -rf venv

	@echo "building virtual enviroment"
	@python3 -m venv venv

	@echo "installing requirements into venv"
	@./venv/bin/pip install -r ../requirements.txt


build: venv/bin/activate ../scripts/build_main.sh
	@mkdir dist
	@$(SHELL) ../scripts/build_main.sh >> ./dist/main.py


clean:
	rm -rf __pycache__
	rm -rf venv
	rm -rf dist
	rm -rf main.py