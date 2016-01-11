#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of addfips.
# http://github.com/fitnr/addfips

# Licensed under the GPL-v3.0 license:
# http://opensource.org/licenses/GPL-3.0
# Copyright (c) 2016, fitnr <fitnr@fakeisthenewreal>

import unittest
import subprocess
import csv
import sys
try:
    import StringIO as io
except ImportError:
    import io

from pkg_resources import resource_filename
from addfips import cli as addfips_cli


class testcli(unittest.TestCase):

    def setUp(self):
        self.states = resource_filename('addfips', 'data/states.csv')
        self.counties = resource_filename('addfips', 'data/counties_2015.csv')

        self.st_args = ['addfips', self.states, '-s', 'name']
        self.co_args = ['addfips', self.counties, '-c', 'name', '-s', 'statefp']

    def testStateCliSubprocess(self):
        p = subprocess.Popen(self.st_args, stdout=subprocess.PIPE)
        out, err = p.communicate()

        assert err is None

        f = io.StringIO(out.decode('utf8'))

        reader = csv.DictReader(f)
        row = next(reader)

        assert row['name'] == 'Alabama'
        assert row['fips'] == '01'

    def testCountyCliSubprocess(self):
        p = subprocess.Popen(self.co_args, stdout=subprocess.PIPE)
        out, err = p.communicate()

        assert err is None

        f = io.StringIO(out.decode('utf-8'))

        reader = csv.DictReader(f)
        row = next(reader)

        assert row['name'] == 'Autauga County'
        assert row['fips'] == '01001'

    def testCountyCliCall(self):
        sys.argv = self.co_args
        sys.stdout = io.StringIO()
        addfips_cli.main()
        sys.stdout.seek(0)
        reader = csv.DictReader(sys.stdout)
        row = next(reader)

        assert row['name'] == 'Autauga County'
        assert row['fips'] == '01001'

    def testStateCliCall(self):
        sys.argv = self.st_args
        sys.stdout = io.StringIO()
        addfips_cli.main()
        sys.stdout.seek(0)
        reader = csv.DictReader(sys.stdout)
        row = next(reader)

        assert row['name'] == 'Alabama'
        assert row['fips'] == '01'

    def testStateNameCliCall(self):
        sys.argv = self.co_args[:-2] + ['--state-name', 'Alabama']
        sys.stdout = io.StringIO()
        addfips_cli.main()
        sys.stdout.seek(0)
        reader = csv.DictReader(sys.stdout)
        row = next(reader)

        assert row['name'] == 'Autauga County'
        assert row['fips'] == '01001'

    def testStateCliCallNoHeader(self):
        sys.argv = self.st_args[:2] + ['-s', '1', '--no-header']
        sys.stdout = io.StringIO()
        addfips_cli.main()
        sys.stdout.seek(0)
        reader = csv.reader(sys.stdout)
        next(reader)
        row = next(reader)

        assert row[1] == 'Alabama'
        assert row[0] == '01'

    def testUnmatched(self):
        assert addfips_cli.unmatched({'fips': None}) is True
        assert addfips_cli.unmatched([None, 'foo']) is True
        assert addfips_cli.unmatched(['01001', 'foo']) is False
        assert addfips_cli.unmatched({'fips': '01001'}) is False

if __name__ == '__main__':
    unittest.main()
