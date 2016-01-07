# This file is part of addfips.
# http://github.com/fitnr/addfips

# Licensed under the GPL-v3.0 license:
# http://opensource.org/licenses/GPL-3.0
# Copyright (c) 2016, fitnr <fitnr@fakeisthenewreal>

import argparse
import csv
import sys
from signal import signal, SIGPIPE, SIG_DFL
from . import __version__ as version
from .addfips import AddFIPS


def positional_fieldnames(args):
    try:
        cf = int(args.county_field)
    except TypeError:
        cf = 0
    try:
        sf = int(args.state_field)
    except TypeError:
        sf = 0
    try:
        ff = int(args.state_fips_field)
    except TypeError:
        ff = 0

    fieldnames = range(0, max(cf, sf, ff))

    if cf:
        fieldnames[cf] = 'county'
    if sf:
        fieldnames[sf] = 'state'
    if ff:
        fieldnames[sf] = 'state_fips_field'

    return fieldnames


def main():
    parser = argparse.ArgumentParser(description="Add FIPS codes to a CSV with state and/or county names")

    parser.add_argument('-V', '--version', action='version', version='%(prog)s ' + version)

    parser.add_argument('INPUT', nargs='?', help='Input file. default: stdin', default='/dev/stdin')
    parser.add_argument('-d', '--delimiter', metavar='CHAR', type=str, default=',', help='field delimiter default: ,', )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument('-s', '--state-field', metavar='FIELD', type=str, help='Read state name or FIPS code from this field')
    group.add_argument('-n', '--state-name', metavar='NAME', type=str, help='Use this state for all rows')

    parser.add_argument('-c', '--county-field', metavar='FIELD', type=str, default=None, help='default: None')
    parser.add_argument('-v', '--vintage', type=str, help='2000 or current')
    parser.add_argument('--no-header', action='store_false', dest='header', help='Has no header now, interpret fields as integers')

    args = parser.parse_args()
    af = AddFIPS(args.vintage)

    if args.header:
        fieldnames = None
    else:
        fieldnames = positional_fieldnames(args)
        args.state_fips_field = 'state_fips_field'

    kwargs = {
        "county_field": args.county_field,
        "state_fips_field": args.state_fips_field,
        "state_field": args.state_field
    }

    if args.county_field and args.state_name:
        kwargs["state_name"] = args.state_name

    with open(args.input) as f:
        reader = csv.DictReader(f, fieldnames=fieldnames)
        signal(SIGPIPE, SIG_DFL)

        fields = ['fips'] + reader.fieldnames

        writer = csv.DictWriter(sys.stdout, fields)
        writer.writeheader()

        for row in reader:
            try:
                if args.county_field:
                    new = af.add_county_fips(row, **kwargs)
                else:
                    new = af.add_state_fips(row, **kwargs)

            except KeyError:
                new = row
                new['fips'] = None

            writer.writerow(new)


if __name__ == '__main__':
    main()
