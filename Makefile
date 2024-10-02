CONTAINERTOOL=podman

.PHONY: build
build:
	python code/_amalgamate.py

.PHONY: readme
readme:
	python clitools.py create --type=readme PACKAGES.md

.PHONY: packages-check
packages-check:
	python clitools.py check --update --commit

.PHONY : test-build
test-build:
	$(CONTAINERTOOL) build -t cli-tools:latest .

.PHONY : test-run
test-run:
	$(CONTAINERTOOL) run --rm -it cli-tools:latest; true

.PHONY : _git_commit_amend
_git_commit_amend:
	git add PACKAGES.md
	git commit --amend --no-edit


.PHONY : pc
pc: | packages-check readme _git_commit_amend

.PHONY : tb
tb: | test-build

.PHONY : tr
tr: | test-run
