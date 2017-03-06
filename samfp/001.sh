#!/bin/csh -f

# General parameters:
#      - You requested to use the following FP: Thickness = 200 microns; tunable gap = 2 microns; p=609 @ Halpha 
#      - You requested to do a CALIBRATION (and not an observation on the sky)
#      - The wavelength (at rest) you gave is             = 6598.95 angstroms
# Interference order:
#      - The interference order @ 6562.78                 = 609.498 
#      - The interference order @ 6598.95                 = 606.157 
#      - The interference order @ 6598.95                 = 606.157 
# Free Spectral Range :
#      - The FSR @ 6598.95 in wavelength                  = 10.8866 Angstrom
#      - The FSR @ 6562.78 in wavelength                  = 10.7675 Angstrom
#      - The FSR @ 6598.95 in thickness                   = 0.329948 microns 
#      - The FSR @ 6598.95 in wavelength                  = 10.8866 Angstrom
#      - The FSR @ 6598.95 in km/s                        = 494.58 km/s
#      - The queensgate constant QGC                      = 18.4473 Angstrom
#      - The FSR in BCV @ 6598.95A                        = 357.72
#      - The FSR in BCV @ 6562.78A                        = 355.759
#      - The FSR in BCV @ 6598.95A                        = 357.72
# Finesse & Scanning:
#      - You gave a real finesse                         = 20.8
#      - Shannon sampling of the finesse                 = 2
#      - Considering F=20.8 and the sampling =2, the float nb of ch to scan for one FSR  = 41.6
#      - Considering F=20.8 and FSR=10.8866, the spectral sampling = 0.523393 Angstroms
#      - The spectral Resolution @ 6598.95 Angstroms        = 12608
#      - The average number of BCV for one FSR             = 8.59904
# Overscanning:
#      - You wanted to scan                                 = 1.2 FSR 
#      - The BCV gap that will be scanned @ 6598.95 Angstro = 429.264
#      - The total number of channels that will be scanned  = 50
#      - The initial BCV value   (nfiniz)                   = 1022
#      - The final BCV value should be around (nfiniz_end)  = 600.647
# SAMI:
#      - You gave nsweeps  = 1
#      - You gave nsteps   = 1
#      - You gave nframe   = 1
#      - You gave exptim per channel             = 0.5 seconds
#      - Readout time per exposure               = 3 seconds 
#      - Total exposure time (whole observation) = 2.91667 minutes
#      - Total exposure time (whole observation) = 0.0486111 hours
#      - You gave binxy                          = 4 
#      - You gave the basename                   = p609_cal

set dat = `date +%Y-%m-%dT%H:%M:%S`
set scid = "SCAN_$dat"
echo "SCAN $scid"
set sweepkey = "FAPERSWP"
set stepkey = "FAPERSST"
set scankey = "FAPERSID"
set nsweeps = 1
set nsteps = 1
set nframe = 1
set nfiniz = 1022
set exptim = 0.5
set binxy = 4
set basename = "p609_cal"
set cmd = `sami dhe set image.dir /home2/images/20170301/001`
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
echo "moving FP to channel 1: BCV=1022"
sami FP moveabs 1022
set sweepid = C001
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 1)"
sami dhe expose
echo
echo "moving FP to channel 2: BCV=1013"
sami FP moveabs 1013
set sweepid = C002
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 2)"
sami dhe expose
echo
echo "moving FP to channel 3: BCV=1005"
sami FP moveabs 1005
set sweepid = C003
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 3)"
sami dhe expose
echo
echo "moving FP to channel 4: BCV=996"
sami FP moveabs 996
set sweepid = C004
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 4)"
sami dhe expose
echo
echo "moving FP to channel 5: BCV=988"
sami FP moveabs 988
set sweepid = C005
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 5)"
sami dhe expose
echo
echo "moving FP to channel 6: BCV=979"
sami FP moveabs 979
set sweepid = C006
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 6)"
sami dhe expose
echo
echo "moving FP to channel 7: BCV=970"
sami FP moveabs 970
set sweepid = C007
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 7)"
sami dhe expose
echo
echo "moving FP to channel 8: BCV=962"
sami FP moveabs 962
set sweepid = C008
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 8)"
sami dhe expose
echo
echo "moving FP to channel 9: BCV=953"
sami FP moveabs 953
set sweepid = C009
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 9)"
sami dhe expose
echo
echo "moving FP to channel 10: BCV=945"
sami FP moveabs 945
set sweepid = C010
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 10)"
sami dhe expose
echo
echo "moving FP to channel 11: BCV=936"
sami FP moveabs 936
set sweepid = C011
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 11)"
sami dhe expose
echo
echo "moving FP to channel 12: BCV=927"
sami FP moveabs 927
set sweepid = C012
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 12)"
sami dhe expose
echo
echo "moving FP to channel 13: BCV=919"
sami FP moveabs 919
set sweepid = C013
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 13)"
sami dhe expose
echo
echo "moving FP to channel 14: BCV=910"
sami FP moveabs 910
set sweepid = C014
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 14)"
sami dhe expose
echo
echo "moving FP to channel 15: BCV=902"
sami FP moveabs 902
set sweepid = C015
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 15)"
sami dhe expose
echo
echo "moving FP to channel 16: BCV=893"
sami FP moveabs 893
set sweepid = C016
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 16)"
sami dhe expose
echo
echo "moving FP to channel 17: BCV=884"
sami FP moveabs 884
set sweepid = C017
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 17)"
sami dhe expose
echo
echo "moving FP to channel 18: BCV=876"
sami FP moveabs 876
set sweepid = C018
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 18)"
sami dhe expose
echo
echo "moving FP to channel 19: BCV=867"
sami FP moveabs 867
set sweepid = C019
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 19)"
sami dhe expose
echo
echo "moving FP to channel 20: BCV=859"
sami FP moveabs 859
set sweepid = C020
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 20)"
sami dhe expose
echo
echo "moving FP to channel 21: BCV=850"
sami FP moveabs 850
set sweepid = C021
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 21)"
sami dhe expose
echo
echo "moving FP to channel 22: BCV=841"
sami FP moveabs 841
set sweepid = C022
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 22)"
sami dhe expose
echo
echo "moving FP to channel 23: BCV=833"
sami FP moveabs 833
set sweepid = C023
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 23)"
sami dhe expose
echo
echo "moving FP to channel 24: BCV=824"
sami FP moveabs 824
set sweepid = C024
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 24)"
sami dhe expose
echo
echo "moving FP to channel 25: BCV=816"
sami FP moveabs 816
set sweepid = C025
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 25)"
sami dhe expose
echo
echo "moving FP to channel 26: BCV=807"
sami FP moveabs 807
set sweepid = C026
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 26)"
sami dhe expose
echo
echo "moving FP to channel 27: BCV=798"
sami FP moveabs 798
set sweepid = C027
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 27)"
sami dhe expose
echo
echo "moving FP to channel 28: BCV=790"
sami FP moveabs 790
set sweepid = C028
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 28)"
sami dhe expose
echo
echo "moving FP to channel 29: BCV=781"
sami FP moveabs 781
set sweepid = C029
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 29)"
sami dhe expose
echo
echo "moving FP to channel 30: BCV=773"
sami FP moveabs 773
set sweepid = C030
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 30)"
sami dhe expose
echo
echo "moving FP to channel 31: BCV=764"
sami FP moveabs 764
set sweepid = C031
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 31)"
sami dhe expose
echo
echo "moving FP to channel 32: BCV=755"
sami FP moveabs 755
set sweepid = C032
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 32)"
sami dhe expose
echo
echo "moving FP to channel 33: BCV=747"
sami FP moveabs 747
set sweepid = C033
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 33)"
sami dhe expose
echo
echo "moving FP to channel 34: BCV=738"
sami FP moveabs 738
set sweepid = C034
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 34)"
sami dhe expose
echo
echo "moving FP to channel 35: BCV=730"
sami FP moveabs 730
set sweepid = C035
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 35)"
sami dhe expose
echo
echo "moving FP to channel 36: BCV=721"
sami FP moveabs 721
set sweepid = C036
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 36)"
sami dhe expose
echo
echo "moving FP to channel 37: BCV=712"
sami FP moveabs 712
set sweepid = C037
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 37)"
sami dhe expose
echo
echo "moving FP to channel 38: BCV=704"
sami FP moveabs 704
set sweepid = C038
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 38)"
sami dhe expose
echo
echo "moving FP to channel 39: BCV=695"
sami FP moveabs 695
set sweepid = C039
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 39)"
sami dhe expose
echo
echo "moving FP to channel 40: BCV=687"
sami FP moveabs 687
set sweepid = C040
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 40)"
sami dhe expose
echo
echo "moving FP to channel 41: BCV=678"
sami FP moveabs 678
set sweepid = C041
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 41)"
sami dhe expose
echo
echo "moving FP to channel 42: BCV=669"
sami FP moveabs 669
set sweepid = C042
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 42)"
sami dhe expose
echo
echo "moving FP to channel 43: BCV=661"
sami FP moveabs 661
set sweepid = C043
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 43)"
sami dhe expose
echo
echo "moving FP to channel 44: BCV=652"
sami FP moveabs 652
set sweepid = C044
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 44)"
sami dhe expose
echo
echo "moving FP to channel 45: BCV=644"
sami FP moveabs 644
set sweepid = C045
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 45)"
sami dhe expose
echo
echo "moving FP to channel 46: BCV=635"
sami FP moveabs 635
set sweepid = C046
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 46)"
sami dhe expose
echo
echo "moving FP to channel 47: BCV=626"
sami FP moveabs 626
set sweepid = C047
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 47)"
sami dhe expose
echo
echo "moving FP to channel 48: BCV=618"
sami FP moveabs 618
set sweepid = C048
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 48)"
sami dhe expose
echo
echo "moving FP to channel 49: BCV=609"
sami FP moveabs 609
set sweepid = C049
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 49)"
sami dhe expose
echo
echo "moving FP to channel 50: BCV=601"
sami FP moveabs 601
set sweepid = C050
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 50)"
sami dhe expose
# Channel: +Step ==> BCV
# [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50]
# [0, -9, -8, -9, -8, -9, -9, -8, -9, -8, -9, -9, -8, -9, -8, -9, -9, -8, -9, -8, -9, -9, -8, -9, -8, -9, -9, -8, -9, -8, -9, -9, -8, -9, -8, -9, -9, -8, -9, -8, -9, -9, -8, -9, -8, -9, -9, -8, -9, -8]
# [1022, 1013, 1005, 996, 988, 979, 970, 962, 953, 945, 936, 927, 919, 910, 902, 893, 884, 876, 867, 859, 850, 841, 833, 824, 816, 807, 798, 790, 781, 773, 764, 755, 747, 738, 730, 721, 712, 704, 695, 687, 678, 669, 661, 652, 644, 635, 626, 618, 609, 601]
