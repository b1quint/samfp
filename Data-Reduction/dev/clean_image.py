# The following two lines are only needed as cosmic.py is not in this directory nor in the python path.
# They would not be required if you copy cosmics.py in this directory.
import sys
sys.path.append("../.") # The directory that contains cosmic.py


import cosmics

# Read the FITS :
array, header = cosmics.fromfits("./data/DARKscaled.fits")
# array is a 2D numpy array

# Build the object :
c = cosmics.cosmicsimage(array, gain=2.1, readnoise=10.0, sigclip = 3.0, sigfrac = 0.3, objlim = 5.0)
# There are other options, check the manual...

# Run the full artillery :
c.run(maxiter = 4)

# Write the cleaned image into a new FITS file, conserving the original header :
cosmics.tofits("clean.fits", c.cleanarray, header)

# If you want the mask, here it is :
cosmics.tofits("mask.fits", c.mask, header)
# (c.mask is a boolean numpy array, that gets converted here to an integer array)