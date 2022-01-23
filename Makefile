# This file is part of addfips.
# http://github.com/fitnr/addfips

# Licensed under the GPL-v3.0 license:
# http://opensource.org/licenses/GPL-3.0
# Copyright (c) 2016, fitnr <fitnr@fakeisthenewreal>

.PHONY: all cov format test publish

all:

cov: | test
	coverage run --branch --source addfips -m unittest
	coverage report

format:
	black src
	isort src
	pylint src

test:
	python -m unittest

publish: build
	twine upload dist/*

build: | clean
	python -m build

clean:; rm -rf dist build
