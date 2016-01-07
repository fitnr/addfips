# This file is part of addfips.
# http://github.com/fitnr/addfips

# Licensed under the GPL-v3.0 license:
# http://opensource.org/licenses/GPL-3.0
# Copyright (c) 2016, fitnr <fitnr@fakeisthenewreal>
from __future__ import print_function
import csv
from pkg_resources import resource_stream

'''
Add county FIPS code to a CSV that has state and county names.
'''

COUNTY_FILES = {
    '2000': 'data/counties_2000.csv',
    'current': 'data/counties_2015.csv'
}

STATES = 'data/states.csv'


class AddFIPS(object):

    """Get a county (and state) FIPS codes."""

    default_county_field = 'county'
    default_state_field = 'state'

    def __init__(self, vintage=None):
        if vintage is None or vintage not in COUNTY_FILES:
            vintage = 'current'

        # load state data
        with resource_stream('addfips', STATES) as f:
            s = list(csv.DictReader(f))
            postals = dict((row['postal'].lower(), row['fips']) for row in s)
            names = dict((row['name'].lower(), row['fips']) for row in s)
            fips = dict((row['fips'], row['fips']) for row in s)
            self.states = dict(postals.items() + names.items() + fips.items())

        # load county data
        with resource_stream('addfips', COUNTY_FILES[vintage]) as f:
            self.counties = dict()

            for row in csv.DictReader(f):
                statefp = row['statefp']

                if statefp not in self.counties:
                    self.counties[statefp] = {}

                name = row['name'].lower()

                self.counties[statefp][name] = row['countyfp']

                if "'" in name:
                    self.counties[statefp][name.replace("'", "")] = row['countyfp']

                # Remove geography name and add to dict
                bare_name = (row['name']
                             .replace(' County', '')
                             .replace(' City', '')
                             .replace(' City and Borough', '')
                             .replace(' Parish', '')
                             .replace(' Census Area', '')
                             .replace(' Borough', '')
                             .replace(' Municipio', '')
                             .replace(' District', '')
                             .lower()
                            )

                self.counties[statefp][bare_name] = row['countyfp']

    def get_state_fips(self, state_name):
        return self.states.get(state_name.lower())

    def get_county_fips(self, county_name, state_name=None, state_fips=None):
        '''
        Get a county's FIPS code.
        :county_name str
        :state_name str Name or postal abbreviation for a state
        :state_fips str State FIPS code
        '''
        if state_name is None and state_fips is None:
            raise KeyError("Need either state name or state FIPS")

        state_fips = state_fips or self.get_state_fips(state_name)
        counties = self.counties.get(state_fips)

        return state_fips + counties[county_name.lower()]

    def add_state_fips(self, row, state_field=None):
        '''
        Add state FIPS to a dictionary.
        :row dict A dictionary with state and county names
        :state_field str name of state name field. default: state
        '''
        state_field = state_field or self.default_state_field
        row['fips'] = self.get_state_fips(row[state_field])
        return row

    def add_county_fips(self, row, county_field=None, state_field=None, state_name=None):
        '''
        Add county FIPS to a dictionary containing a state name, FIPS code, or using a passed state name or FIPS code.
        :row dict A dictionary with state and county names
        :county_field str county name field. default: county
        :state_fips_field str state FIPS field containing state fips
        :state_field str state name field. default: county
        :state_name str State name or FIPS code to use
        '''
        if state_name:
            state_fips = self.get_state_fips(state_name)
        else:
            state_fips = self.get_state_fips(row[state_field])

        county = row[county_field or self.default_county_field]
        row['fips'] = self.get_county_fips(county, state_fips=state_fips)

        return row
