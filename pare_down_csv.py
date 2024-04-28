import sys
import csv
from collections import defaultdict

import argparse
from datetime import datetime


def pare_down(input_filename, output_filename, time=0, start=None, end=None, verbose=0):
    last_hour = None
    last_seen = defaultdict(lambda: datetime.strptime('20000101', '%Y%m%d'))
    with open(sys.argv[2], 'w') as newfile:
        with open(sys.argv[1], newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',')
            for row in spamreader:
                new_date = datetime.strptime(row[1], '%Y%m%d %H:%M:%S')
                if verbose > 0 and (last_hour is None or (last_hour < new_date and last_hour.hour != new_date.hour)):
                    last_hour = new_date
                    print(f'\rProcessing {datetime.strftime(last_hour, "%m/%d/%Y %H")}:00:00', end='')
                if start is not None and new_date < start:
                    continue
                if end is not None and end < new_date:
                    continue
                if (new_date - last_seen[row[0]]).total_seconds() > time:
                    last_seen[row[0]] = new_date
                    print(','.join(row), file=newfile)


def parse_args():
    parser = argparse.ArgumentParser(
            prog='Pare down',
            description='Paring down large CTA data dumps',
            epilog='Konstantinos Ameranis 2024')
    parser.add_argument('input_filename', type=str, help='File to read from')
    parser.add_argument('output_filename', type=str, help='File to save results to')
    parser.add_argument('-t', '--time', type=int, default=0, help='Minimum time in seconds between data points. For example, 30 would mean additional observations within 30 seconds are going to be passed up. Default is 0 to mean no observations are discarded')
    parser.add_argument('-s', '--start', type=str, default=None, help='Start time to clip the dataset. Should be either in "20240428 12:00:00" or "20240428" format')
    parser.add_argument('-e', '--end', type=str, default=None, help='End time to clip the dataset. Should be either in "20240428 12:00:00" or "20240428" format')
    parser.add_argument('-v', '--verbose', default=0, action='count', help='Verbosity of output')
    args = parser.parse_args()

    # Verify arguments
    if args.input_filename == args.output_filename:
        print('Operation would overwrite input filename. Aborting...', file=sys.stderr)
        sys.exit(1)
    if args.time < 0:
        print('Argument time cannot be negative. Aborting...', file=sys.stderr)
        sys.exit(1)
    if args.start is not None:
        try:
            args.start = datetime.strptime(args.start, '%Y%m%d %H:%M:%S')
        except ValueError:
            pass
        try:
            args.start = datetime.strptime(args.start, '%Y%m%d')
        except ValueError:
            print('Unable to parse start time. Aborting...')
            sys.exit(1)

    if args.end is not None:
        try:
            args.end = datetime.strptime(args.end, '%Y%m%d %H:%M:%S')
        except ValueError:
            pass
        try:
            args.end = datetime.strptime(args.end, '%Y%m%d')
        except ValueError:
            print('Unable to parse end time. Aborting...')
            sys.exit(1)
    return args


def main():
    args = parse_args()
    pare_down(args.input_filename, args.output_filename, args.time, args.start, args.end, args.verbose)


if __name__ == '__main__':
    main()
