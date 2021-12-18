.PHONY: check_programs run clean build dist

all : check_programs build

python = $(shell PATH=$(PATH) which python3)
python ?= $(shell PATH=$(PATH) which python)

os = $(shell ../scripts/get_backend.sh -p $(python) -g os)
backend = $(shell ../scripts/get_backend.sh -p $(python) -g backend)

mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
current_dir := $(notdir $(patsubst %/,%,$(dir $(mkfile_path))))


check_programs:
	@echo "checking system"
	@echo                found python : $(python)
	@echo buiding with backend for os : $(os)


venv/bin/activate: ../requirements.txt
	@rm -rf __pycache__
	@rm -rf venv
	@rm -rf dist
	@rm -rf main.py

	@echo "building virtual enviroment"
	@python3 -m venv venv

	@echo "installing requirements into venv"
	@./venv/bin/pip install -r ../requirements.txt

ifdef $(dist)
distt:
	@echo
else
	@echo creating dist
	@mkdir dist
distt:
	@echo hello
endif


build: distt venv/bin/activate ../scripts/build_main.sh
	@echo "creating main file"
	@$(SHELL) ../scripts/build_main.sh >> ./dist/main.py


run: build
	$(shell ./venv/bin/python ./dist/main.py)


clean:
	@echo "removing __pycache__"
	@rm -rf __pycache__
	@echo "removing venv"
	@rm -rf venv
	@echo "removing dist"
	@rm -rf dist
	@echo "removing main.py"
	@rm -rf main.py