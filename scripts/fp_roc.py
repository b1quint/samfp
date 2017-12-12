#!python

import os
import sys

import argparse
from samfp.tools import ztools

parser = argparse.ArgumentParser(description="Repeats a data-cube [N] times.")

parser.add_argument(
    'input_cube',
    type=str,
    help="Input cube."
)

parser.add_argument(
    'output_cube',
    type=str,
    help="Output cube."
)

parser.add_argument(
    'oversample_factor',
    type=int,
    help="Oversample factor."
)

parser.add_argument(
    '--kind',
    '-k',
    type=str,
    default='linear',
    choices=['linear'],
    help="Oversample factor."
)

parser.add_argument(
    '--n_begin_repeat',
    type=int,
    default=0,
    help="Add 'n' copies of the cube in its beginning (affects header)."
)

parser.add_argument(
    '--n_end_repeat',
    type=int,
    default=0,
    help="Add 'n' copies of the cube in its end (affects header)."
)

parser.add_argument(
    '--n_begin_cut',
    type=int,
    default=None,
    help="Cut channel at the beginning of the cube where "
         "[BEGIN] is the index of the channel number starting "
         "from 0."
)

parser.add_argument(
    '--n_end_cut',
    type=int,
    default=None,
    help="Cut channel at the end of the cube. Use negative "
         "values to count the channels backwards (e.g. -10 "
         "excludes the last 10 channels).")

args = parser.parse_args()

# Check before running
if not os.path.exists(args.input_cube):
    print("\n Input file does not exists: %s\n Leaving now." % args.input_cube)
    sys.exit(1)

if os.path.exists(args.output_cube):
    print("\n Output file exists: %s" % args.output_cube)
    print(" Delete it before running this.\n Leaving now.")
    sys.exit(1)

fp_repeat = ztools.ZRepeat(
    args.input_cube,
    '.fp_repeat.temp.fits',
    n_after=args.n_end_repeat,
    n_before=args.n_begin_repeat
)

fp_repeat.start()
fp_repeat.join()

fp_repeat = ztools.ZOversample(
    '.fp_repeat.temp.fits',
    '.fp_oversample.temp.fits',
    args.oversample_factor,
    kind=args.kind
)

fp_repeat.start()
fp_repeat.join()

fp_cut = ztools.ZCut(
    '.fp_oversample.temp.fits',
    args.output_cube,
    n_begin=args.n_begin_cut,
    n_end=args.n_end_cut
)

fp_cut.start()
fp_cut.join()

os.remove('.fp_repeat.temp.fits')
os.remove('.fp_oversample.temp.fits')

print('Finished all.\n\n\n')