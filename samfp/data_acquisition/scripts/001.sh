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
#      - The queensgate constant QGC                      = 18.854 Angstrom
#      - The FSR in BCV @ 6598.953A                        = 350.000
#      - The FSR in BCV @ 6562.780A                        = 348.081
#      - The FSR in BCV @ 6598.953A                        = 350.000
# Finesse & Scanning:
#      - You gave a real finesse                         = 18.000
#      - Shannon sampling of the finesse                 = 2.500
#      - Considering F=18.000 and the sampling =2.500, the float nb of ch to scan for one FSR  = 45.000
#      - Considering F=18.000 and FSR=10.887, the spectral sampling = 0.605 Angstroms
#      - The spectral Resolution @ 6598.953 Angstroms        = 10910.000
#      - The average number of BCV for one channel             = 7.778
# Overscanning:
#      - You wanted to scan 1.200 FSR 
#      - The BCV gap that will be scanned @ 6598.953 Angstro = 420.000
#      - The total number of channels that will be scanned  = 55.000
#      - The initial BCV value   (nfiniz)                   = 1024.000
#      - The final BCV value should be around (nfiniz_end)  = 604.000
# SAMI:
#      - You gave nsweeps  = 1
#      - You gave nsteps   = 1
#      - You gave nframe   = 1
#      - You gave exptim per channel             = 0.500 seconds
#      - Readout time per exposure               = 2.000 seconds 
#      - Total exposure time (whole observation) = 2.292 minutes
#      - Total exposure time (whole observation) = 0.038 hours
#      - You gave binxy                          = 4 
#      - You gave the basename                   = ne_6600

set dat = `date +%Y-%m-%dT%H:%M:%S`
set scid = "SCAN_$dat"
echo "SCAN $scid"
set sweepkey = "FAPERSWP"
set stepkey = "FAPERSST"
set scankey = "FAPERSID"
set nsweeps = 1
set nsteps = 1
set nframe = 1
set nfiniz = 1024
set exptim = 0.5
set binxy = 4
set basename = "cal_Ne-BTFI6600-20"
set cmd = `sami dhe set image.dir /home2/images/SAMFP/20170301/001`
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
echo "moving FP to channel 1: BCV=1024"
sami FP moveabs 1024
set sweepid = C001
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 1)"
sami dhe expose
echo
echo "moving FP to channel 2: BCV=1016"
sami FP moveabs 1016
set sweepid = C002
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 2)"
sami dhe expose
echo
echo "moving FP to channel 3: BCV=1008"
sami FP moveabs 1008
set sweepid = C003
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 3)"
sami dhe expose
echo
echo "moving FP to channel 4: BCV=1001"
sami FP moveabs 1001
set sweepid = C004
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 4)"
sami dhe expose
echo
echo "moving FP to channel 5: BCV=993"
sami FP moveabs 993
set sweepid = C005
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 5)"
sami dhe expose
echo
echo "moving FP to channel 6: BCV=985"
sami FP moveabs 985
set sweepid = C006
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 6)"
sami dhe expose
echo
echo "moving FP to channel 7: BCV=977"
sami FP moveabs 977
set sweepid = C007
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 7)"
sami dhe expose
echo
echo "moving FP to channel 8: BCV=970"
sami FP moveabs 970
set sweepid = C008
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 8)"
sami dhe expose
echo
echo "moving FP to channel 9: BCV=962"
sami FP moveabs 962
set sweepid = C009
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 9)"
sami dhe expose
echo
echo "moving FP to channel 10: BCV=954"
sami FP moveabs 954
set sweepid = C010
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 10)"
sami dhe expose
echo
echo "moving FP to channel 11: BCV=946"
sami FP moveabs 946
set sweepid = C011
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 11)"
sami dhe expose
echo
echo "moving FP to channel 12: BCV=938"
sami FP moveabs 938
set sweepid = C012
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 12)"
sami dhe expose
echo
echo "moving FP to channel 13: BCV=931"
sami FP moveabs 931
set sweepid = C013
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 13)"
sami dhe expose
echo
echo "moving FP to channel 14: BCV=923"
sami FP moveabs 923
set sweepid = C014
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 14)"
sami dhe expose
echo
echo "moving FP to channel 15: BCV=915"
sami FP moveabs 915
set sweepid = C015
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 15)"
sami dhe expose
echo
echo "moving FP to channel 16: BCV=907"
sami FP moveabs 907
set sweepid = C016
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 16)"
sami dhe expose
echo
echo "moving FP to channel 17: BCV=900"
sami FP moveabs 900
set sweepid = C017
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 17)"
sami dhe expose
echo
echo "moving FP to channel 18: BCV=892"
sami FP moveabs 892
set sweepid = C018
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 18)"
sami dhe expose
echo
echo "moving FP to channel 19: BCV=884"
sami FP moveabs 884
set sweepid = C019
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 19)"
sami dhe expose
echo
echo "moving FP to channel 20: BCV=876"
sami FP moveabs 876
set sweepid = C020
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 20)"
sami dhe expose
echo
echo "moving FP to channel 21: BCV=868"
sami FP moveabs 868
set sweepid = C021
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 21)"
sami dhe expose
echo
echo "moving FP to channel 22: BCV=861"
sami FP moveabs 861
set sweepid = C022
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 22)"
sami dhe expose
echo
echo "moving FP to channel 23: BCV=853"
sami FP moveabs 853
set sweepid = C023
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 23)"
sami dhe expose
echo
echo "moving FP to channel 24: BCV=845"
sami FP moveabs 845
set sweepid = C024
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 24)"
sami dhe expose
echo
echo "moving FP to channel 25: BCV=837"
sami FP moveabs 837
set sweepid = C025
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 25)"
sami dhe expose
echo
echo "moving FP to channel 26: BCV=830"
sami FP moveabs 830
set sweepid = C026
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 26)"
sami dhe expose
echo
echo "moving FP to channel 27: BCV=822"
sami FP moveabs 822
set sweepid = C027
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 27)"
sami dhe expose
echo
echo "moving FP to channel 28: BCV=814"
sami FP moveabs 814
set sweepid = C028
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 28)"
sami dhe expose
echo
echo "moving FP to channel 29: BCV=806"
sami FP moveabs 806
set sweepid = C029
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 29)"
sami dhe expose
echo
echo "moving FP to channel 30: BCV=798"
sami FP moveabs 798
set sweepid = C030
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 30)"
sami dhe expose
echo
echo "moving FP to channel 31: BCV=791"
sami FP moveabs 791
set sweepid = C031
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 31)"
sami dhe expose
echo
echo "moving FP to channel 32: BCV=783"
sami FP moveabs 783
set sweepid = C032
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 32)"
sami dhe expose
echo
echo "moving FP to channel 33: BCV=775"
sami FP moveabs 775
set sweepid = C033
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 33)"
sami dhe expose
echo
echo "moving FP to channel 34: BCV=767"
sami FP moveabs 767
set sweepid = C034
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 34)"
sami dhe expose
echo
echo "moving FP to channel 35: BCV=760"
sami FP moveabs 760
set sweepid = C035
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 35)"
sami dhe expose
echo
echo "moving FP to channel 36: BCV=752"
sami FP moveabs 752
set sweepid = C036
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 36)"
sami dhe expose
echo
echo "moving FP to channel 37: BCV=744"
sami FP moveabs 744
set sweepid = C037
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 37)"
sami dhe expose
echo
echo "moving FP to channel 38: BCV=736"
sami FP moveabs 736
set sweepid = C038
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 38)"
sami dhe expose
echo
echo "moving FP to channel 39: BCV=728"
sami FP moveabs 728
set sweepid = C039
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 39)"
sami dhe expose
echo
echo "moving FP to channel 40: BCV=721"
sami FP moveabs 721
set sweepid = C040
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 40)"
sami dhe expose
echo
echo "moving FP to channel 41: BCV=713"
sami FP moveabs 713
set sweepid = C041
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 41)"
sami dhe expose
echo
echo "moving FP to channel 42: BCV=705"
sami FP moveabs 705
set sweepid = C042
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 42)"
sami dhe expose
echo
echo "moving FP to channel 43: BCV=697"
sami FP moveabs 697
set sweepid = C043
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 43)"
sami dhe expose
echo
echo "moving FP to channel 44: BCV=690"
sami FP moveabs 690
set sweepid = C044
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 44)"
sami dhe expose
echo
echo "moving FP to channel 45: BCV=682"
sami FP moveabs 682
set sweepid = C045
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 45)"
sami dhe expose
echo
echo "moving FP to channel 46: BCV=674"
sami FP moveabs 674
set sweepid = C046
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 46)"
sami dhe expose
echo
echo "moving FP to channel 47: BCV=666"
sami FP moveabs 666
set sweepid = C047
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 47)"
sami dhe expose
echo
echo "moving FP to channel 48: BCV=658"
sami FP moveabs 658
set sweepid = C048
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 48)"
sami dhe expose
echo
echo "moving FP to channel 49: BCV=651"
sami FP moveabs 651
set sweepid = C049
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 49)"
sami dhe expose
echo
echo "moving FP to channel 50: BCV=643"
sami FP moveabs 643
set sweepid = C050
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 50)"
sami dhe expose
echo
echo "moving FP to channel 51: BCV=635"
sami FP moveabs 635
set sweepid = C051
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 51)"
sami dhe expose
echo
echo "moving FP to channel 52: BCV=627"
sami FP moveabs 627
set sweepid = C052
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 52)"
sami dhe expose
echo
echo "moving FP to channel 53: BCV=620"
sami FP moveabs 620
set sweepid = C053
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 53)"
sami dhe expose
echo
echo "moving FP to channel 54: BCV=612"
sami FP moveabs 612
set sweepid = C054
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 54)"
sami dhe expose
echo
echo "moving FP to channel 55: BCV=604"
sami FP moveabs 604
set sweepid = C055
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 55)"
sami dhe expose
# Channel: +Step ==> BCV
# [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55]
# [0, -8, -8, -7, -8, -8, -8, -7, -8, -8, -8, -8, -7, -8, -8, -8, -7, -8, -8, -8, -8, -7, -8, -8, -8, -7, -8, -8, -8, -8, -7, -8, -8, -8, -7, -8, -8, -8, -8, -7, -8, -8, -8, -7, -8, -8, -8, -8, -7, -8, -8, -8, -7, -8, -8]
# [1024, 1016, 1008, 1001, 993, 985, 977, 970, 962, 954, 946, 938, 931, 923, 915, 907, 900, 892, 884, 876, 868, 861, 853, 845, 837, 830, 822, 814, 806, 798, 791, 783, 775, 767, 760, 752, 744, 736, 728, 721, 713, 705, 697, 690, 682, 674, 666, 658, 651, 643, 635, 627, 620, 612, 604]
