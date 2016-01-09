#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of addfips.
# http://github.com/fitnr/addfips

# Licensed under the GPL-v3.0 license:
# http://opensource.org/licenses/GPL-3.0
# Copyright (c) 2016, fitnr <fitnr@fakeisthenewreal>

import unittest
from addfips import addfips


class testbase(unittest.TestCase):

    def setUp(self):
        self.af = addfips.AddFIPS()
        self.row = {
            'county': 'Kings',
            'borough': 'Brooklyn',
            'state': 'New York',
            'statefp': '36',
            'foo': 'bar'
        }
        self.list = ['Kings', 'Brooklyn', 'New York', 'NY', '36']

    def testBasics(self):
        assert isinstance(self.af._states, dict)
        assert isinstance(self.af._counties, dict)

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
        self.assertEqual(self.af.get_county_fips('Añasco Municipio', 'PR'), "72011")
        self.assertEqual(self.af.get_county_fips('Añasco', 'PR'), "72011")

    def testMunicipality(self):
        self.assertEqual(self.af.get_county_fips('Anchorage Municipality', 'AK'), "02020")
        self.assertEqual(self.af.get_county_fips('Anchorage', 'AK'), "02020")

        assert self.af.get_county_fips('Northern Islands', '69') == "69085"

    def testCity(self):
        assert self.af.get_county_fips('Emporia', 'Virginia') == "51595"

    def testSaint(self):
        assert self.af.get_county_fips('St. Clair County', 'AL') == "01115"
        assert self.af.get_county_fips('St. Clair', 'AL') == "01115"
        assert self.af.get_county_fips('St. Louis City', 'Missouri') == "29510"
        self.assertEqual(self.af.get_county_fips('Saint Louis County', 'Missouri'), "29189")
        assert self.af.get_county_fips('Saint Louis County', 'MO') == "29189"
        assert self.af.get_county_fips('Saint Louis City', 'MO') == "29510"

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

    def testVintages(self):
        assert 2000 in addfips.COUNTY_FILES
        assert 2010 in addfips.COUNTY_FILES
        assert 2015 in addfips.COUNTY_FILES

    def testVintage2015(self):
        self.assertIsNone(self.af.get_county_fips('Clifton Forge', 'VA'))

    def testVintage2010(self):
        af2010 = addfips.AddFIPS(vintage=2010)
        assert af2010.get_county_fips('Wade Hampton', 'Alaska') == '02270'
        self.assertIsNone(af2010.get_county_fips('Clifton Forge', 'VA'))

    def testVintage2000(self):
        af2000 = addfips.AddFIPS(vintage=2000)
        assert af2000.get_county_fips('Wade Hampton', 'Alaska') == '02270'
        self.assertEqual(af2000.get_county_fips('Clifton Forge city', 'Virginia'), "51560")
        assert af2000.get_county_fips('Clifton Forge', 'Virginia') == "51560"



if __name__ == '__main__':
    unittest.main()
