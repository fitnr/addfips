#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of addfips.
# http://github.com/fitnr/addfips

# Licensed under the GPL-v3.0 license:
# http://opensource.org/licenses/GPL-3.0
# Copyright (c) 2016, fitnr <fitnr@fakeisthenewreal>

import unittest
from addfips import AddFIPS


class testbase(unittest.TestCase):

    def setUp(self):
        self.af = AddFIPS()
        self.row = {
            'county': 'Kings',
            'borough': 'Brooklyn',
            'state': 'New York',
            'statefp': '36',
            'foo': 'bar'
        }

    def testBasics(self):
        assert isinstance(self.af.states, dict)
        assert isinstance(self.af.counties, dict)

    def testGetCounty(self):
        assert self.af.get_state_fips('New York') == '36'
        assert self.af.get_state_fips('36') == '36'
        assert self.af.get_state_fips('NY') == '36'
        assert self.af.get_state_fips('ny') == '36'
        assert self.af.get_state_fips('new york') == '36'

    def testKeyErrors(self):
        with self.assertRaises(KeyError):
            self.af.get_county_fips('foo')

        with self.assertRaises(KeyError):
            self.af.get_county_fips('foo', state_name='New York')

    def testCountyRow(self):
        new = self.af.add_county_fips(self.row, county_field='county', state_field='state')
        assert new['fips'] == '36047'
        assert new['foo'] == 'bar'

        new = self.af.add_county_fips(self.row, county_field='county', state_field='statefp')
        assert new['fips'] == '36047'

        new = self.af.add_county_fips(self.row, county_field='borough', state_field='statefp')
        assert new['fips'] == '36047'

    def testCountyRowStateName(self):
        new = self.af.add_county_fips(self.row, county_field='county', state_name='New York')
        assert new['fips'] == '36047'
        assert new['foo'] == 'bar'

    def testStateRow(self):
        new = self.af.add_state_fips(self.row, state_field='state')
        assert new['fips'] == '36'
        assert new['foo'] == 'bar'

        new = self.af.add_state_fips(self.row, state_field='statefp')
        assert new['fips'] == '36'


if __name__ == '__main__':
    unittest.main()
