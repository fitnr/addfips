# Add FIPS

Add FIPS is a tool for adding state or county FIPS codes to files that contain just the names of those geographies.

FIPS codes are the official ID numbers of places in the US. They're invaluable for matching data from different sources.

Say you have a CSV file like this:

```
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

## Installing

Add FIPS is a Python package, compatible with Python 2.7, Python 3, and pypy. It has no dependencies outside of Python's standard libraries.

If you've used Python packages before:
```
pip install addfips
# or
pip install --user addfips
```

If you haven't used Python packages before, [get pip](http://pip.readthedocs.org/en/stable/installing/), then come back.

You can also clone the repo and install with `python setup.py install`.

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

### Examples

Add state FIPS codes:
````
addfips data.csv --state-field fieldName > data_with_fips.csv
````

Add state and county FIPS codes:
````
addfips data.csv --state-field fieldName --county-field countyName > data_with_fips.csv
````

Use field index for a file with no header row:
```
addfips data_no_header.csv --no-header-row -s 1 > data_no_header_fips.csv
```

Add FIPS for counties from a specific state. These are equivalent:
```
addfips ny_data.csv --state-name NY -c county > ny_data_fips.csv
addfips ny_data.csv --state-name 'New York' -c county > ny_data_fips.csv
addfips ny_data.csv --state-name 36 -c county > ny_data_fips.csv
```

Use an alternate delimiter:
```
addfips pipe_delimited.dsv -d'|' -s state > result.csv
addfips semicolon_delimited.dsv -d';' -s state > result.csv
```

Pipe from other programs:
````
curl http://example.com/data.csv | addfips -s stateFieldName -c countyField > data_with_fips.csv
csvkit -c state,county,important huge_file.csv | addfips -s state -c county > small_file.csv
````

Pipe to other programs. In files with extensive text, filtering with the FIPS code is safer than using county names, which may be common words (e.g. cook):
````
addfips culinary_data.csv -s stateFieldName -c countyField | grep -e "^17031" > culinary_data_cook_county.csv
addfips -s StateName -c CountyName data.csv | csvsort -c fips > sorted_by_fips.csv
````

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

The results of `AddFIPS.get_state_fips` and `AddFIPS.get_county_fips` are strings, since FIPS codes may have leading zeros.

#### AddFIPS(vintage='current')

__get_state_fips(self, state)__
Returns two-digit FIPS code based on  a state name or postal code.

__get_county_fips(self, county, state)__
Returns five-digit FIPS code based on county name and state name/abbreviation/FIPS.

__add_state_fips(self, row, state_field='state')__
Returns the input row with a two-figit state FIPS code added.
Input row may be either a `dict` or a `list`. If a `dict`, the 'fips' key is added. If a `list`, the FIPS code is added at the start of the list.

__add_county_fips(self, row, county_field='county', state_field='state', state=None)__
Returns the input row with a five-figit county FIPS code added.
Input row may be either a `dict` or a `list`. If a `dict`, the 'fips' key is added. If a `list`, the FIPS code is added at the start of the list.

### License
Distributed under the GNU General Public License, version 3. See LICENSE for more information.
