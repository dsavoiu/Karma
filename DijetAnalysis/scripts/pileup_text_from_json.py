#!/usr/bin/env python
import argparse
import json
import os


def _do(file_path_in, file_path_out):
    with open(file_path_in, 'r') as f:
        data = json.load(f)

    with open(file_path_out, 'w') as f:
        for run, run_data in data.iteritems():
            for ls_data in run_data:
                ls, a, b, c = ls_data
                f.write("{:s} {:d} {:g} {:g} {:g}\n".format(run, ls, a, b, c))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Convert `pileup_latest.txt` file from JSON to simple columnar format (space-separated).')

    parser.add_argument(
        'FILE_IN',
        type=str,
        help="JSON-format `pileup_latest.txt` file",
    )
    parser.add_argument(
        'FILE_OUT',
        type=str,
        help="output file",
    )
    args = parser.parse_args()

    if os.path.exists(args.FILE_OUT):
        raise IOError("Output file exists ({}). Aborting.".format(args.FILE_OUT))

    _do(args.FILE_IN, args.FILE_OUT)
