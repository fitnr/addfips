# This file is part of addfips.
# http://github.com/fitnr/addfips
# Licensed under the GPL-v3.0 license:
# http://opensource.org/licenses/GPL-3.0
# Copyright (c) 2016, fitnr <fitnr@fakeisthenewreal>

"""Add FIPS codes to a CSV with state and/or county names."""

import argparse
import csv
import sys
from signal import SIG_DFL, SIGPIPE, signal

from . import __version__ as version, VINTAGES
from .addfips import AddFIPS


def unmatched(result):
    """Check if fips is defined in a result row."""
    try:
        if result['fips'] is None:
            return True
    except TypeError:
        if result[0] is None:
            return True

    return False


def main():
    """Add FIPS codes to a CSV with state and/or county names."""
    parser = argparse.ArgumentParser(description="Add FIPS codes to a CSV with state and/or county names")
    parser.add_argument('-V', '--version', action='version', version='%(prog)s ' + version)

    parser.add_argument('input', nargs='?', help='Input file. default: stdin')
    parser.add_argument('-d', '--delimiter', metavar='CHAR', type=str, help='field delimiter. default: ,')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-s', '--state-field', metavar='FIELD', type=str, help='Read state name or FIPS code from this field'
    )
    group.add_argument('-n', '--state-name', metavar='NAME', type=str, help='Use this state for all rows')

    parser.add_argument(
        '-c',
        '--county-field',
        metavar='FIELD',
        type=str,
        help='Read county name from this field. If blank, only state FIPS code will be added',
    )
    parser.add_argument('-v', '--vintage', choices=VINTAGES, help='Data era. Default: 2020')
    parser.add_argument(
        '--no-header', action='store_false', dest='header', help='Input has no header now, interpret fields as integers'
    )
    parser.add_argument(
        '-u', '--err-unmatched', action='store_true', help='Print rows that addfips cannot match to stderr'
    )

    parser.set_defaults(delimiter=',', input='/dev/stdin')

    args = parser.parse_args()
    addfips = AddFIPS(args.vintage)

    kwargs = {
        # This may be None, and that's ... OK.
        "state_field": args.state_field
    }

    # Check if we're decoding counties or states.
    if args.county_field:
        func = addfips.add_county_fips
        kwargs["county_field"] = args.county_field
        if args.state_name:
            kwargs["state"] = args.state_name

    else:
        func = addfips.add_state_fips

    with open(args.input, 'rt', encoding="utf8") as f:
        signal(SIGPIPE, SIG_DFL)

        if args.header:
            # Read the header, write a header.
            reader = csv.DictReader(f, delimiter=args.delimiter)
            fields = ['fips'] + reader.fieldnames
            writer = csv.DictWriter(sys.stdout, fields)
            writer.writeheader()

            if args.err_unmatched:
                error = csv.DictWriter(sys.stderr, fields)

        else:
            # Don't read a header, don't write a header.
            kwargs['state_field'] = int(kwargs['state_field']) - 1

            if 'county_field' in kwargs:
                kwargs['county_field'] = int(kwargs.get('county_field')) - 1

            reader = csv.reader(f, delimiter=args.delimiter)
            writer = csv.writer(sys.stdout)

            if args.err_unmatched:
                error = csv.writer(sys.stderr)

        # Write results, optionally to stderr
        for row in reader:
            result = func(row, **kwargs)

            if args.err_unmatched and unmatched(result):
                error.writerow(row)
            else:
                writer.writerow(result)


if __name__ == '__main__':
    main()
