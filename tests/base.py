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
        self.list = ['Kings', 'Brooklyn', 'New York', 'NY', '36']

    def testBasics(self):
        assert isinstance(self.af.states, dict)
        assert isinstance(self.af.counties, dict)

    def testGetState(self):
        assert self.af.get_state_fips('New York') == '36'
        assert self.af.get_state_fips('36') == '36'
        assert self.af.get_state_fips('NY') == '36'
        assert self.af.get_state_fips('ny') == '36'
        assert self.af.get_state_fips('new york') == '36'

    def testGetCounty(self):
        # Full County Name with various ways of ID'ing state
        assert self.af.get_county_fips("Val Verde County", '48') == "48465"
        assert self.af.get_county_fips("Johnson County", 'Kansas') == "20091"
        assert self.af.get_county_fips("Fall River County", "SD") == "46047"

    def testCaseInsensitive(self):
        assert self.af.get_county_fips('niagara', 'ny') == '36063'

    def testNoCounty(self):
        assert self.af.get_county_fips("El Dorado", 'California') == "06017"

    def testParish(self):
        assert self.af.get_county_fips('Acadia Parish', 'Louisiana') == "22001"
        assert self.af.get_county_fips('Caldwell', 'Louisiana') == "22021"

    def testAlaskaBoroughs(self):
        assert self.af.get_county_fips('Aleutians East', 'AK') == "02013"
        assert self.af.get_county_fips("Juneau", "Alaska") == "02110"

    def testNYCBoroughs(self):
        assert self.af.get_county_fips("Brooklyn", "NY") == "36047"

    def testDiacretics(self):
        assert self.af.get_county_fips('Dona Ana', '35') == "35013"
        assert self.af.get_county_fips('Añasco Municipio', 'Puerto Rico') == "72011"

    def testMunicipios(self):
        assert self.af.get_county_fips('Anasco', 'PR') == "72011"

    def testCity(self):
        assert self.af.get_county_fips('Emporia', 'Virginia') == "51595"

    def testSaint(self):
        assert self.af.get_county_fips('St. Louis', 'Missouri') == "29510"
        assert self.af.get_county_fips('Saint Louis', 'MO') == "29510"

    def testDistrict(self):
        assert self.af.get_county_fips("Manu'a District", "60") == "60020"

    def testEmpty(self):
        assert self.af.get_county_fips('foo', 'bar') is None
        assert self.af.get_county_fips('foo', state='New York') is None
        assert self.af.get_state_fips('foo') is None

    def testCountyRowDict(self):
        new = self.af.add_county_fips(self.row, county_field='county', state_field='state')
        assert new['fips'] == '36047'
        assert new['foo'] == 'bar'

        new = self.af.add_county_fips(self.row, county_field='county', state_field='statefp')
        assert new['fips'] == '36047'

        new = self.af.add_county_fips(self.row, county_field='borough', state_field='statefp')
        assert new['fips'] == '36047'

    def testCountyRowDictDefaults(self):
        new = self.af.add_county_fips(self.row)
        assert new['fips'] == '36047'

        self.af.default_state_field = 'statefp'
        self.af.default_county_field = 'borough'
        new = self.af.add_county_fips(self.row)
        assert new['fips'] == '36047'

    def testCountyRowList(self):
        new = self.af.add_county_fips(self.list, county_field=1, state_field=2)
        assert new[0] == '36047'

    def testCountyRowStateName(self):
        new = self.af.add_county_fips(self.row, county_field='county', state='New York')
        assert new['fips'] == '36047'
        assert new['foo'] == 'bar'

    def testStateRow(self):
        new = self.af.add_state_fips(self.row, state_field='state')
        assert new['fips'] == '36'
        assert new['foo'] == 'bar'

        new = self.af.add_state_fips(self.row, state_field='statefp')
        assert new['fips'] == '36'

    def testStateList(self):
        new = self.af.add_state_fips(self.list, state_field=2)
        assert new[0] == '36'

        new = self.af.add_state_fips(self.list, state_field=3)
        assert new[0] == '36'


if __name__ == '__main__':
    unittest.main()
