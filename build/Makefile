.PHONY: check_programs run clean build

all : check_programs

python = $(shell PATH=$(PATH) which python3)
python ?= $(shell PATH=$(PATH) which python)

os = $(shell ../scripts/get_backend.sh -p $(python) -g os)
backend = $(shell ../scripts/get_backend.sh -p $(python) -g backend)


check_programs:
	@echo "checking system"
	@echo                found python : $(python)
	@echo buiding with backend for os : $(os)


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