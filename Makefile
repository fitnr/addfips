# This file is part of addfips.
# http://github.com/fitnr/addfips

# Licensed under the GPL-v3.0 license:
# http://opensource.org/licenses/GPL-3.0
# Copyright (c) 2016, fitnr <fitnr@fakeisthenewreal>

.PHONY: test format cov deploy

cov: | test
	coverage report
	coverage html

format:
	black addfips
	pylint addfips

test:
	coverage run --source addfips -m unittest tests/*.py

deploy:
	twine register
	git push; git push --tags
	rm -rf dist build
	python3 setup.py bdist_wheel --python-tag py3
	python3 setup.py sdist
	twine upload dist/*
