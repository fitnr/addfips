# Add FIPS

Add FIPS is a tool for adding county FIPS codes to files that contain county and state names.

FIPS codes are the official ID numbers of places in the US. They're invaluable for matching data from  different sources.

Say you have a CSV file like this:

```csv
state,county,statistic
IL,Cook,123
California,Los Angeles County,321
New York,Kings,137
LA,Orleans,99
Alaska,Kusilvak,12
```

Add FIPS lets you do this:
```
> addfips --county-field=county input.csv
countyfp,state,county,statistic
17031,IL,Cook,123
06037,California,Los Angeles County,321
36047,New York,Kings,137
22071,LA,Orleans,99
02270,Alaska,Kusilvak,12
```

## Install

Add FIPS is a Python package.

```
pip install addfips
```

Works in Python 2.7, 3, and pypy.

## Features

* Use full names or postal abbrevations for states
* Works with all states, territories, and the District of Columbia
* Fuzzy matching allows for missing diacretic marks and different name formats ('Nye County' or 'Nye')

(Note that Baltimore city and Baltimore County need to be properly named. Behavior for just passing "Baltimore" is undefined.)

## Command line tool
````
usage: addfips [-h] [-V] [-d CHAR] (-s FIELD | -n NAME) [-c FIELD]
               [-v VINTAGE] [--no-header]
               [input]

Add FIPS codes to a CSV with state and/or county names

positional arguments:
  input                 Input file. default: stdin

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  -d CHAR, --delimiter CHAR
                        field delimiter default: ,
  -s FIELD, --state-field FIELD
                        Read state name or FIPS code from this field
  -n NAME, --state-name NAME
                        Use this state for all rows
  -c FIELD, --county-field FIELD
                        default: None
  -v VINTAGE, --vintage VINTAGE
                        2000 or current
  --no-header           Has no header now, interpret fields as integers
````

Options and flags:
* `input`: (positional argument) The name of the file. If blank, `addfips` reads from stdin.
* `--delimiter`: Field delimiter, defaults to ','.
* `--state-field`: Name of the field containing state name
* `--state-name`: Name, postal abbreviation or state FIPS code to use for all rows.
* `--county-field`: Name of the field containing county name. If this is blank, the output will contain the two-character state FIPS code.
* `--vintage`: pass 2000 to use 2000 county names
* `--no-header`: Indicates that the input file has no header. `--state-field` and `--county-field` are parsed as field indices.


## API

Add fips is available for use in your Python scripts:
````python
>>> import addfips
>>> af = addfips.AddFIPS()
>>> af.get_state_fips('Puerto Rico')
'72'
>>> af.get_county_fips('Nye', state_name='Nevada')
'32023'
>>> row = {'county': 'Cook County', 'state': 'IL'}
>>> af.add_county_fips(row, county_field="county", state_field="state")
{'county': 'Cook County', 'state': 'IL', 'fips': '17031'}
````

### `AddFIPS(vintage='current')`

#### get_state_fips(self, state)
Returns two-digit FIPS code based on  a state name or postal code.

#### get_county_fips(self, county, state)
Returns five-digit FIPS code based on county name and state name/abbreviation/FIPS.

#### add_state_fips(self, row, state_field=None)
Returns the input row with a two-figit state FIPS code added.
Input row may be either a `dict` or a `list`. If a `dict`, the 'fips' key is added. If a `list`, the FIPS code is added at the start of the list.

#### add_county_fips(self, row, county_field=None, state_field=None, state=None)
Returns the input row with a five-figit county FIPS code added.
Input row may be either a `dict` or a `list`. If a `dict`, the 'fips' key is added. If a `list`, the FIPS code is added at the start of the list.

### License
Distributed under the GNU General Public License, version 3. See LICENSE for more information.
