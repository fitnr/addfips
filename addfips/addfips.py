# This file is part of addfips.
# http://github.com/fitnr/addfips

# Licensed under the GPL-v3.0 license:
# http://opensource.org/licenses/GPL-3.0
# Copyright (c) 2016, fitnr <fitnr@fakeisthenewreal>
import csv
import re
from pkg_resources import resource_filename

'''
Add county FIPS code to a CSV that has state and county names.
'''

COUNTY_FILES = {
    2000: 'data/counties_2000.csv',
    2010: 'data/counties_2010.csv',
    2015: 'data/counties_2015.csv',
}

STATES = 'data/states.csv'


class AddFIPS(object):

    """Get state or county FIPS codes"""

    default_county_field = 'county'
    default_state_field = 'state'

    def __init__(self, vintage=None):
        if vintage is None or vintage not in COUNTY_FILES:
            vintage = max(COUNTY_FILES.keys())

        # load state data
        state_csv = resource_filename('addfips', STATES)
        with open(state_csv, 'rt') as f:
            s = list(csv.DictReader(f))
            postals = dict((row['postal'].lower(), row['fips']) for row in s)
            names = dict((row['name'].lower(), row['fips']) for row in s)
            fips = dict((row['fips'], row['fips']) for row in s)
            self._state_fips = frozenset(fips)
            self._states = dict(list(postals.items()) + list(names.items()) + list(fips.items()))

        # load county data
        county_pattern = r' (County|city|City|City and Borough|Borough|Census Area|Municipio|District|Parish)$'
        county_csv = resource_filename('addfips', COUNTY_FILES[vintage])
        with open(county_csv, 'rt') as f:
            self._counties = dict()

            for row in csv.DictReader(f):
                statefp = row['statefp']

                if statefp not in self._counties:
                    self._counties[statefp] = {}

                name = row['name'].lower()

                self._counties[statefp][name] = row['countyfp']

                if "'" in name:
                    self._counties[statefp][name.replace("'", "")] = row['countyfp']

                # Remove geography name and add to dict
                bare_name = re.sub(county_pattern, '', row['name']).lower()

                self._counties[statefp][bare_name] = row['countyfp']

    def get_state_fips(self, state):
        '''Get FIPS code from a state name or postal code'''
        if state is None:
            return None

        # Check if we already have a FIPS code
        if state in self._state_fips:
            return state

        return self._states.get(state.lower())

    def get_county_fips(self, county, state):
        '''
        Get a county's FIPS code.
        :county str County name
        :state str Name, postal abbreviation or FIPS code for a state
        '''
        state_fips = self.get_state_fips(state)
        counties = self._counties.get(state_fips, {})

        try:
            return state_fips + counties.get(county.lower())
        except TypeError:
            return None

    def add_state_fips(self, row, state_field=None):
        '''
        Add state FIPS to a dictionary.
        :row dict/list A dictionary with state and county names
        :state_field str name of state name field. default: state
        '''
        state_field = state_field or self.default_state_field
        fips = self.get_state_fips(row[state_field])

        try:
            row['fips'] = fips
        except TypeError:
            row.insert(0, fips)
        return row

    def add_county_fips(self, row, county_field=None, state_field=None, state=None):
        '''
        Add county FIPS to a dictionary containing a state name, FIPS code, or using a passed state name or FIPS code.
        :row dict/list A dictionary with state and county names
        :county_field str county name field. default: county
        :state_fips_field str state FIPS field containing state fips
        :state_field str state name field. default: county
        :state str State name, postal abbreviation or FIPS code to use
        '''
        if state:
            state_fips = self.get_state_fips(state)
        else:
            state_fips = self.get_state_fips(row[state_field or self.default_state_field])

        if county_field is None:
            county_field = self.default_county_field

        fips = self.get_county_fips(row[county_field], state_fips)

        try:
            row['fips'] = fips
        except TypeError:
            row.insert(0, fips)

        return row
