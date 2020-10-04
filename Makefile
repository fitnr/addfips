# This file is part of addfips.
# http://github.com/fitnr/addfips

# Licensed under the GPL-v3.0 license:
# http://opensource.org/licenses/GPL-3.0
# Copyright (c) 2016, fitnr <fitnr@fakeisthenewreal>

.PHONY: test cov

cov: | test
	coverage html

format:
	black addfips
	pylint addfips

test:
	coverage run --include=addfips/* setup.py test

deploy:
	twine register
	git push; git push --tags
	rm -rf dist build
	python3 setup.py bdist_wheel --universal
	twine upload dist/*
