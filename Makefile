CONTAINERTOOL=podman

.PHONY: build
build:
	python code/_amalgate.py

.PHONY: readme
readme:
	python clitools.py create --type=readme PACKAGES.md

.PHONY: packages-check
packages-check:
	python clitools.py check

.PHONY : test-build
test-build:
	$(CONTAINERTOOL) build -t cli-tools:latest .

.PHONY : test-run
test-run:
	$(CONTAINERTOOL) run --rm -it cli-tools:latest; true


.PHONY : pc
pc: | packages-check

.PHONY : tb
tb: | test-build

.PHONY : tr
tr: | test-run
