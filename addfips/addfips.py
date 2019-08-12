# -*- coding: utf-8 -*-
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

COUNTY_PATTERN = r' (county|city|city and borough|borough|census area|municipio|municipality|district|parish)$'


class AddFIPS(object):

    """Get state or county FIPS codes"""

    default_county_field = 'county'
    default_state_field = 'state'

    diacretics = {
        r"ñ": "n",
        r"'": "",
        r"ó": "o",
        r"í": "i",
        r"á": "a",
        r"ü": "u",
        r"é": "e",
        r"î": "i",
        r"è": "e",
        r"à": "a",
        r"ì": "i",
        r"å": "a",
    }

    abbrevs = {
        'ft. ': 'fort ',
        'st. ': 'saint ',
        'ste. ': 'sainte ',
    }

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

        # Handle de-diacreticizing
        self.diacretic_pattern = '(' + ('|'.join(self.diacretics)) + ')'
        self.delete_diacretics = lambda x: self.diacretics[x.group()]

        # load county data
        county_csv = resource_filename('addfips', COUNTY_FILES[vintage])
        with open(county_csv, 'rt') as f:
            self._counties = dict()
            self._counties_by_fips = dict()

            for row in csv.DictReader(f):
                fips = str(row['statefp']) + str(row['countyfp'])
                if not self._counties_by_fips.get(fips, None):
                    self._counties_by_fips[int(fips)] = row['name']

                if row['statefp'] not in self._counties:
                    self._counties[row['statefp']] = {}

                state = self._counties[row['statefp']]

                # Strip diacretics, remove geography name and add both to dict
                county = self._delete_diacretics(row['name'].lower())
                bare_county = re.sub(COUNTY_PATTERN, '', county)
                state[county] = state[bare_county] = row['countyfp']

                # Add both versions of abbreviated names to the dict.
                for short, full in self.abbrevs.items():
                    needle, replace = None, None

                    if county.startswith(short):
                        needle, replace = short, full
                    elif county.startswith(full):
                        needle, replace = full, short

                    if needle is not None:
                        replaced = county.replace(needle, replace, 1)
                        bare_replaced = bare_county.replace(needle, replace, 1)
                        state[replaced] = state[bare_replaced] = row['countyfp']

    def _delete_diacretics(self, string):
        return re.sub(self.diacretic_pattern, self.delete_diacretics, string)

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
            name = self._delete_diacretics(county.lower())
            return state_fips + counties.get(name)
        except TypeError:
            return None

    def get_county_by_fips(self, fips):
        '''Get county name from FIPS code'''

        if self._counties_by_fips.get(fips, None):
            return self._counties_by_fips.get(fips, None)

    def add_state_fips(self, row, state_field=None):
        '''
        Add state FIPS to a dictionary.
        :row dict/list A dictionary with state and county names
        :state_field str name of state name field. default: state
        '''
        if state_field is None:
            state_field = self.default_state_field

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
