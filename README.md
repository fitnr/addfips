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

## Features

* Use full names or postal abbrevations for states
* Works with all states, territories, and the District of Columbia
* Fuzzy matching allows for missing diacretic marks and different name formats ('Nye County' or 'Nye')

(Note that Baltimore city and Baltimore County need to be properly named. Behavior for just passing "Baltimore" is undefined.)