.PHONY: check_programs run clean

all : check_programs run


# EXECUTABLES := python
# K := $(foreach exec,$(EXECUTABLES),\
	$(if $(shell PATH=$(PATH) which $(exec)),some string,$(error "No $(exec) in PATH")))

check_programs:
	@echo $(shell PATH=$(PATH) which python3)

venv/bin/activate: ../requirements.txt
	python3 -m venv venv
	./venv/bin/pip install -r ../requirements.txt

run: venv/bin/activate
	./venv/bin/python3 ../src/main.py

clean:
	rm -rf __pycache__
	rm -rf venv