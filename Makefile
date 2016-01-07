# This file is part of addfips.
# http://github.com/fitnr/addfips

# Licensed under the GPL-v3.0 license:
# http://opensource.org/licenses/GPL-3.0
# Copyright (c) 2016, fitnr <fitnr@fakeisthenewreal>

# show coverage in html format
cov:
	coverage run --include addfips/* setup.py test
	coverage html

deploy: README.rst
	git push; git push --tags
	rm -rf dist build
	python setup.py register
	python setup.py sdist
	python3 setup.py bdist_wheel
	twine upload dist/*

README.rst: README.md
	- pandoc $< -o $@
	@touch $@
	python setup.py check -r -s -m -q
