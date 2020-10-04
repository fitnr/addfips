# -*- coding: utf-8 -*-
# This file is part of addfips.
# http://github.com/fitnr/addfips

# Licensed under the GPL-v3.0 license:
# http://opensource.org/licenses/GPL-3.0
# Copyright (c) 2016, fitnr <fitnr@fakeisthenewreal>
'''
Add county FIPS code to a CSV that has state and county names.
'''
import csv
import re

from importlib_resources import files

COUNTY_FILES = {
    2000: 'data/counties_2000.csv',
    2010: 'data/counties_2010.csv',
    2015: 'data/counties_2015.csv',
    2020: 'data/counties_2015.csv',
}

STATES = 'data/states.csv'

COUNTY_PATTERN = r" (county|city|city and borough|borough|census area|municipio|municipality|district|parish)$"

DIACRETICS = {
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
ABBREVS = {
    'ft. ': 'fort ',
    'st. ': 'saint ',
    'ste. ': 'sainte ',
}


class AddFIPS:

    """Get state or county FIPS codes"""

    default_county_field = 'county'
    default_state_field = 'state'
    data = files('addfips')

    def __init__(self, vintage=None):
        # Handle de-diacreticizing
        self.diacretic_pattern = '(' + ('|'.join(DIACRETICS)) + ')'
        self.delete_diacretics = lambda x: DIACRETICS[x.group()]

        if vintage is None or vintage not in COUNTY_FILES:
            vintage = max(COUNTY_FILES.keys())

        self._states, self._state_fips = self._load_state_data()

        self._counties = self._load_county_data(vintage)

    def _load_state_data(self):
        with self.data.joinpath(STATES).open('rt') as f:
            reader = csv.DictReader(f)
            states = {}
            state_fips = {}
            for row in reader:
                states[row['postal'].lower()] = row['fips']
                states[row['name'].lower()] = row['fips']
                state_fips[row['fips']] = row['fips']

            state_fips = frozenset(state_fips)

        return states, state_fips

    def _load_county_data(self, vintage):
        with self.data.joinpath(COUNTY_FILES[vintage]).open('rt') as f:
            counties = {}
            for row in csv.DictReader(f):
                if row['statefp'] not in counties:
                    counties[row['statefp']] = {}

                state = counties[row['statefp']]

                # Strip diacretics, remove geography name and add both to dict
                county = self._delete_diacretics(row['name'].lower())
                bare_county = re.sub(COUNTY_PATTERN, '', county)
                state[county] = state[bare_county] = row['countyfp']

                # Add both versions of abbreviated names to the dict.
                for short, full in ABBREVS.items():
                    needle, replace = None, None

                    if county.startswith(short):
                        needle, replace = short, full
                    elif county.startswith(full):
                        needle, replace = full, short

                    if needle is not None:
                        replaced = county.replace(needle, replace, 1)
                        bare_replaced = bare_county.replace(needle, replace, 1)
                        state[replaced] = state[bare_replaced] = row['countyfp']
        return counties

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
        """
        Get a county's FIPS code.
        :county str County name
        :state str Name, postal abbreviation or FIPS code for a state
        """
        state_fips = self.get_state_fips(state)
        counties = self._counties.get(state_fips, {})

        try:
            name = self._delete_diacretics(county.lower())
            return state_fips + counties.get(name)
        except TypeError:
            return None

    def add_state_fips(self, row, state_field=None):
        """
        Add state FIPS to a dictionary.
        :row dict/list A dictionary with state and county names
        :state_field str name of state name field. default: state
        """
        if state_field is None:
            state_field = self.default_state_field

        fips = self.get_state_fips(row[state_field])

        try:
            row['fips'] = fips
        except TypeError:
            row.insert(0, fips)
        return row

    def add_county_fips(self, row, county_field=None, state_field=None, state=None):
        """
        Add county FIPS to a dictionary containing a state name, FIPS code, or using a passed state name or FIPS code.
        :row dict/list A dictionary with state and county names
        :county_field str county name field. default: county
        :state_fips_field str state FIPS field containing state fips
        :state_field str state name field. default: county
        :state str State name, postal abbreviation or FIPS code to use
        """
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
