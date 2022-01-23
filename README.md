# AddFIPS

AddFIPS is a tool for adding state or county FIPS codes to files that contain just the names of those geographies.

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

AddFIPS lets you do this:
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

AddFIPS is a Python package compatible with versions 3.7+.

If you've used Python packages before:
```
pip install addfips
# or
pip install --user addfips
```

If you haven't used Python packages before, [get pip](http://pip.readthedocs.org/en/stable/installing/), then come back.

## Features

* Use full names or postal abbrevations for states
* Works with all states, territories, and the District of Columbia
* Slightly fuzzy matching allows for missing diacretic marks and different name formats ("Nye County" or "Nye', "Saint Louis" or "St. Louis", "Prince George's" or "Prince Georges")
* Includes up-to-date 2015 geographies (shout out to Kusilvak Census Area, AK, and Oglala Lakota Co., SD)

Note that some states have counties and county-equivalent independent cities with the same names (e.g. Baltimore city & County, MD, Richmond city & County, VA). AddFIPS's behavior may pick the wrong geography if just the name ("Baltimore") is passed.

## Command line tool
````
usage: addfips [-h] [-V] [-d CHAR] (-s FIELD | -n NAME) [-c FIELD]
               [-v VINTAGE] [--no-header]
               [input]

AddFIPS codes to a CSV with state and/or county names

positional arguments:
  input                 Input file. default: stdin

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  -d CHAR, --delimiter CHAR
                        field delimiter. default: ,
  -s FIELD, --state-field FIELD
                        Read state name or FIPS code from this field
  -n NAME, --state-name NAME
                        Use this state for all rows
  -c FIELD, --county-field FIELD
                        Read county name from this field. If blank, only state
                        FIPS code will be added
  -v VINTAGE, --vintage VINTAGE
                        2000, 2010, or 2015. default: 2015
  --no-header           Input has no header now, interpret fields as integers
  -u, --err-unmatched   Print rows that addfips cannot match to stderr
````

Options and flags:
* `input`: (positional argument) The name of the file. If blank, `addfips` reads from stdin.
* `--delimiter`: Field delimiter, defaults to ','.
* `--state-field`: Name of the field containing state name
* `--state-name`: Name, postal abbreviation or state FIPS code to use for all rows.
* `--county-field`: Name of the field containing county name. If this is blank, the output will contain the two-character state FIPS code.
* `--vintage`: Use earlier county names and FIPS codes. For instance, Clifton Forge city, VA, is not included in 2010 or later vintages.
* `--no-header`: Indicates that the input file has no header. `--state-field` and `--county-field` are parsed as field indices.
* `--err-unmatched`: Rows that `addfips` cannot match will be printed to stderr, rather than stdout

The output is a CSV with a new column, "fips", appended to the front. When `addfips` cannot make a match, the fips column will have an empty value.

### Examples

Add state FIPS codes:
````
addfips data.csv --state-field fieldName > data_with_fips.csv
````

Add state and county FIPS codes:
````
addfips data.csv --state-field fieldName --county-field countyName > data_with_fips.csv
````

For files with no header row, use a number to refer to the columns with state and/or county names:
```
addfips --no-header-row --state-field 1 --county-field 2 data_no_header.csv > data_no_header_fips.csv
```

Column numbers are one-indexed.

AddFIPS for counties from a specific state. These are equivalent:
```
addfips ny_data.csv -c county --state-name NY > ny_data_fips.csv
addfips ny_data.csv -c county --state-name 'New York' > ny_data_fips.csv
addfips ny_data.csv -c county --state-name 36 > ny_data_fips.csv
```

Use an alternate delimiter:
```
addfips -d'|' -s state pipe_delimited.dsv > result.csv
addfips -d';' -s state semicolon_delimited.dsv > result.csv
```

Print unmatched rows to another file:
```
addfips --err-unmatched -s state state_data.csv > state_data_fips.csv 2> state_unmatched.csv
addfips -u -s STATE -c COUNTY county_data.csv > county_data_fips.csv 2> county_unmatched.csv
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

AddFIPS is available for use in your Python scripts:
````python
>>> import addfips
>>> af = addfips.AddFIPS()
>>> af.get_state_fips('Puerto Rico')
'72'
>>> af.get_county_fips('Nye', state='Nevada')
'32023'
>>> row = {'county': 'Cook County', 'state': 'IL'}
>>> af.add_county_fips(row, county_field="county", state_field="state")
{'county': 'Cook County', 'state': 'IL', 'fips': '17031'}
````

The results of `AddFIPS.get_state_fips` and `AddFIPS.get_county_fips` are strings, since FIPS codes may have leading zeros.

### Classes

#### AddFIPS(vintage=None)

The AddFIPS class takes one keyword argument, `vintage`, which may be either `2000`, `2010` or `2015`. Any other value will use the most recent vintage. Other vintages may be added in the future.

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
