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
try:
    import StringIO as io
except ImportError:
    import io

from pkg_resources import resource_filename


class testcli(unittest.TestCase):
    def setUp(self):
        self.states = resource_filename('addfips', 'data/states.csv')
        self.counties = resource_filename('addfips', 'data/counties_2015.csv')

    def testStateCli(self):
        args = ['addfips', self.states, '-s', 'name']
        p = subprocess.Popen(args, stdout=subprocess.PIPE)

        out, err = p.communicate()

        assert err is None

        f = io.StringIO(out.decode('utf8'))

        reader = csv.DictReader(f)
        row = next(reader)

        assert row['name'] == 'Alabama'
        assert row['fips'] == '01'

    def testCountyCli(self):
        args = ['addfips', self.counties, '-s', 'statefp', '-c', 'name']
        p = subprocess.Popen(args, stdout=subprocess.PIPE)

        out, err = p.communicate()

        assert err is None

        f = io.StringIO(out.decode('utf-8'))

        reader = csv.DictReader(f)
        row = next(reader)

        assert row['name'] == 'Autauga County'
        assert row['fips'] == '01001'
