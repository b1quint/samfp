#!/bin/csh -f

# General parameters:
#      - You requested to use the following FP: Thickness = 200 microns; tunable gap = 2 microns; p=609 @ Halpha} 
#      - You requested to do a CALIBRATION (and not an observation on the sky)
#      - The wavelength (at rest) you gave is             = 6598.953 angstroms
# Interference order:
#      - The interference order @ 6562.780                 = 609.498 
#      - The interference order @ 6598.953                 = 606.157 
#      - The interference order @ 6598.953                 = 606.157 
# Free Spectral Range :
#      - The FSR @ 6598.953 in wavelength                  = 10.887 Angstrom
#      - The FSR @ 6562.780 in wavelength                  = 10.768 Angstrom
#      - The FSR @ 6598.953 in thickness                   = 0.330 microns 
#      - The FSR @ 6598.953 in wavelength                  = 10.887 Angstrom
#      - The FSR @ 6598.953 in km/s                        = 494.580 km/s
#      - The queensgate constant QGC                      = 18.330 Angstrom
#      - The FSR in BCV @ 6598.953A                        = 360.000
#      - The FSR in BCV @ 6562.780A                        = 358.027
#      - The FSR in BCV @ 6598.953A                        = 360.000
# Finesse & Scanning:
#      - You gave a real finesse                         = 17.000
#      - Shannon sampling of the finesse                 = 2.100
#      - Considering F=17.000 and the sampling =2.100, the float nb of ch to scan for one FSR  = 35.700
#      - Considering F=17.000 and FSR=10.887, the spectral sampling = 0.640 Angstroms
#      - The spectral Resolution @ 6598.953 Angstroms        = 10304.000
#      - The average number of BCV for one channel             = 10.084
# Overscanning:
#      - You wanted to scan 1.100 FSR 
#      - The BCV gap that will be scanned @ 6598.953 Angstro = 396.000
#      - The total number of channels that will be scanned  = 40.000
#      - The initial BCV value   (nfiniz)                   = 768.000
#      - The final BCV value should be around (nfiniz_end)  = 374.723
# SAMI:
#      - You gave nsweeps  = 1
#      - You gave nsteps   = 1
#      - You gave nframe   = 1
#      - You gave exptim per channel             = 1.000 seconds
#      - Readout time per exposure               = 2.000 seconds 
#      - Total exposure time (whole observation) = 2.000 minutes
#      - Total exposure time (whole observation) = 0.033 hours
#      - You gave binxy                          = 4 
#      - You gave the basename                   = calA

set dat = `date +%Y-%m-%dT%H:%M:%S`
set scid = "SCAN_$dat"
echo "SCAN $scid"
set sweepkey = "FAPERSWP"
set stepkey = "FAPERSST"
set scankey = "FAPERSID"
set nsweeps = 1
set nsteps = 1
set nframe = 1
set nfiniz = 768
set exptim = 1.0
set binxy = 4
set basename = "calA"
set cmd = `sami dhe set image.dir /home2/images/SAMFP/20170301/004`
set cmd = `sami dhe dbs set $scankey $scid`
set cmd = `sami dhe dbs set $stepkey custom`
echo "setting number of images, exposure time and basename"
sami dhe set binning $binxy $binxy
sami dhe set obs.nimages $nframe
sami dhe set obs.exptime $exptim
sami dhe set image.basename $basename
echo
echo "image $basename, exptime $exptim"
echo "binning $binxy"
echo
echo "moving FP to channel 1: BCV=768"
sami FP moveabs 768
set sweepid = C001
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 1)"
sami dhe expose
echo
echo "moving FP to channel 2: BCV=758"
sami FP moveabs 758
set sweepid = C002
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 2)"
sami dhe expose
echo
echo "moving FP to channel 3: BCV=748"
sami FP moveabs 748
set sweepid = C003
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 3)"
sami dhe expose
echo
echo "moving FP to channel 4: BCV=738"
sami FP moveabs 738
set sweepid = C004
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 4)"
sami dhe expose
echo
echo "moving FP to channel 5: BCV=728"
sami FP moveabs 728
set sweepid = C005
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 5)"
sami dhe expose
echo
echo "moving FP to channel 6: BCV=718"
sami FP moveabs 718
set sweepid = C006
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 6)"
sami dhe expose
echo
echo "moving FP to channel 7: BCV=707"
sami FP moveabs 707
set sweepid = C007
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 7)"
sami dhe expose
echo
echo "moving FP to channel 8: BCV=697"
sami FP moveabs 697
set sweepid = C008
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 8)"
sami dhe expose
echo
echo "moving FP to channel 9: BCV=687"
sami FP moveabs 687
set sweepid = C009
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 9)"
sami dhe expose
echo
echo "moving FP to channel 10: BCV=677"
sami FP moveabs 677
set sweepid = C010
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 10)"
sami dhe expose
echo
echo "moving FP to channel 11: BCV=667"
sami FP moveabs 667
set sweepid = C011
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 11)"
sami dhe expose
echo
echo "moving FP to channel 12: BCV=657"
sami FP moveabs 657
set sweepid = C012
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 12)"
sami dhe expose
echo
echo "moving FP to channel 13: BCV=647"
sami FP moveabs 647
set sweepid = C013
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 13)"
sami dhe expose
echo
echo "moving FP to channel 14: BCV=637"
sami FP moveabs 637
set sweepid = C014
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 14)"
sami dhe expose
echo
echo "moving FP to channel 15: BCV=627"
sami FP moveabs 627
set sweepid = C015
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 15)"
sami dhe expose
echo
echo "moving FP to channel 16: BCV=617"
sami FP moveabs 617
set sweepid = C016
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 16)"
sami dhe expose
echo
echo "moving FP to channel 17: BCV=607"
sami FP moveabs 607
set sweepid = C017
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 17)"
sami dhe expose
echo
echo "moving FP to channel 18: BCV=597"
sami FP moveabs 597
set sweepid = C018
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 18)"
sami dhe expose
echo
echo "moving FP to channel 19: BCV=586"
sami FP moveabs 586
set sweepid = C019
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 19)"
sami dhe expose
echo
echo "moving FP to channel 20: BCV=576"
sami FP moveabs 576
set sweepid = C020
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 20)"
sami dhe expose
echo
echo "moving FP to channel 21: BCV=566"
sami FP moveabs 566
set sweepid = C021
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 21)"
sami dhe expose
echo
echo "moving FP to channel 22: BCV=556"
sami FP moveabs 556
set sweepid = C022
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 22)"
sami dhe expose
echo
echo "moving FP to channel 23: BCV=546"
sami FP moveabs 546
set sweepid = C023
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 23)"
sami dhe expose
echo
echo "moving FP to channel 24: BCV=536"
sami FP moveabs 536
set sweepid = C024
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 24)"
sami dhe expose
echo
echo "moving FP to channel 25: BCV=526"
sami FP moveabs 526
set sweepid = C025
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 25)"
sami dhe expose
echo
echo "moving FP to channel 26: BCV=516"
sami FP moveabs 516
set sweepid = C026
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 26)"
sami dhe expose
echo
echo "moving FP to channel 27: BCV=506"
sami FP moveabs 506
set sweepid = C027
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 27)"
sami dhe expose
echo
echo "moving FP to channel 28: BCV=496"
sami FP moveabs 496
set sweepid = C028
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 28)"
sami dhe expose
echo
echo "moving FP to channel 29: BCV=486"
sami FP moveabs 486
set sweepid = C029
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 29)"
sami dhe expose
echo
echo "moving FP to channel 30: BCV=476"
sami FP moveabs 476
set sweepid = C030
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 30)"
sami dhe expose
echo
echo "moving FP to channel 31: BCV=465"
sami FP moveabs 465
set sweepid = C031
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 31)"
sami dhe expose
echo
echo "moving FP to channel 32: BCV=455"
sami FP moveabs 455
set sweepid = C032
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 32)"
sami dhe expose
echo
echo "moving FP to channel 33: BCV=445"
sami FP moveabs 445
set sweepid = C033
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 33)"
sami dhe expose
echo
echo "moving FP to channel 34: BCV=435"
sami FP moveabs 435
set sweepid = C034
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 34)"
sami dhe expose
echo
echo "moving FP to channel 35: BCV=425"
sami FP moveabs 425
set sweepid = C035
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 35)"
sami dhe expose
echo
echo "moving FP to channel 36: BCV=415"
sami FP moveabs 415
set sweepid = C036
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 36)"
sami dhe expose
echo
echo "moving FP to channel 37: BCV=405"
sami FP moveabs 405
set sweepid = C037
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 37)"
sami dhe expose
echo
echo "moving FP to channel 38: BCV=395"
sami FP moveabs 395
set sweepid = C038
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 38)"
sami dhe expose
echo
echo "moving FP to channel 39: BCV=385"
sami FP moveabs 385
set sweepid = C039
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 39)"
sami dhe expose
echo
echo "moving FP to channel 40: BCV=375"
sami FP moveabs 375
set sweepid = C040
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 40)"
sami dhe expose
# Channel: +Step ==> BCV
# [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40]
# [0, -10, -10, -10, -10, -10, -11, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -11, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -11, -10, -10, -10, -10, -10, -10, -10, -10, -10]
# [768, 758, 748, 738, 728, 718, 707, 697, 687, 677, 667, 657, 647, 637, 627, 617, 607, 597, 586, 576, 566, 556, 546, 536, 526, 516, 506, 496, 486, 476, 465, 455, 445, 435, 425, 415, 405, 395, 385, 375]
