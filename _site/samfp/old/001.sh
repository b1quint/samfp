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
#      - The queensgate constant QGC                      = 18.3304 Angstrom
#      - The FSR in BCV @ 6598.95A                        = 360
#      - The FSR in BCV @ 6562.78A                        = 358.027
#      - The FSR in BCV @ 6598.95A                        = 360
# Finesse & Scanning:
#      - You gave a real finesse                         = 30.46
#      - Shannon sampling of the finesse                 = 2
#      - Considering F=30.46 and the sampling =2, the float nb of ch to scan for one FSR  = 60.92
#      - Considering F=30.46 and FSR=10.8866, the spectral sampling = 0.357406 Angstroms
#      - The spectral Resolution @ 6598.95 Angstroms        = 18463
#      - The average number of BCV for one FSR             = 5.90939
#      - The maximum number of BCV that the CS100 can jump at once = 3
# Overscanning:
#      - You wanted to scan                                 = 1.1 FSR 
#      - The BCV gap that will be scanned @ 6598.95 Angstro = 396
#      - The total number of channels that will be scanned  = 68
#      - The initial BCV value   (nfiniz)                   = 1024
#      - The final BCV value should be around (nfiniz_end)  = 628.071
# SAMI:
#      - You gave nsweeps  = 1
#      - You gave nsteps   = 1
#      - You gave nframe   = 1
#      - You gave exptim per channel             = 10 seconds
#      - Readout time per exposure               = 3 seconds 
#      - Total exposure time (whole observation) = 14.7333 minutes
#      - Total exposure time (whole observation) = 0.245556 hours
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
set nfiniz = 1024
set exptim = 10.0
set binxy = 4
set basename = "p609_cal"
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
echo "moving FP to BCV 1021 "
sami FP moveabs 1021
sleep 1
echo
echo "moving FP to channel 2: BCV=1018"
sami FP moveabs 1018
set sweepid = C002
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 2)"
sami dhe expose
echo
echo "moving FP to BCV 1015 "
sami FP moveabs 1015
sleep 1
echo
echo "moving FP to channel 3: BCV=1012"
sami FP moveabs 1012
set sweepid = C003
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 3)"
sami dhe expose
echo
echo "moving FP to BCV 1009 "
sami FP moveabs 1009
sleep 1
echo
echo "moving FP to channel 4: BCV=1006"
sami FP moveabs 1006
set sweepid = C004
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 4)"
sami dhe expose
echo
echo "moving FP to BCV 1003 "
sami FP moveabs 1003
sleep 1
echo
echo "moving FP to channel 5: BCV=1000"
sami FP moveabs 1000
set sweepid = C005
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 5)"
sami dhe expose
echo
echo "moving FP to BCV 997 "
sami FP moveabs 997
sleep 1
echo
echo "moving FP to channel 6: BCV=994"
sami FP moveabs 994
set sweepid = C006
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 6)"
sami dhe expose
echo
echo "moving FP to BCV 991 "
sami FP moveabs 991
sleep 1
echo
echo "moving FP to channel 7: BCV=989"
sami FP moveabs 989
set sweepid = C007
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 7)"
sami dhe expose
echo
echo "moving FP to BCV 986 "
sami FP moveabs 986
sleep 1
echo
echo "moving FP to channel 8: BCV=983"
sami FP moveabs 983
set sweepid = C008
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 8)"
sami dhe expose
echo
echo "moving FP to BCV 980 "
sami FP moveabs 980
sleep 1
echo
echo "moving FP to channel 9: BCV=977"
sami FP moveabs 977
set sweepid = C009
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 9)"
sami dhe expose
echo
echo "moving FP to BCV 974 "
sami FP moveabs 974
sleep 1
echo
echo "moving FP to channel 10: BCV=971"
sami FP moveabs 971
set sweepid = C010
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 10)"
sami dhe expose
echo
echo "moving FP to BCV 968 "
sami FP moveabs 968
sleep 1
echo
echo "moving FP to channel 11: BCV=965"
sami FP moveabs 965
set sweepid = C011
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 11)"
sami dhe expose
echo
echo "moving FP to BCV 962 "
sami FP moveabs 962
sleep 1
echo
echo "moving FP to channel 12: BCV=959"
sami FP moveabs 959
set sweepid = C012
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 12)"
sami dhe expose
echo
echo "moving FP to BCV 956 "
sami FP moveabs 956
sleep 1
echo
echo "moving FP to channel 13: BCV=953"
sami FP moveabs 953
set sweepid = C013
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 13)"
sami dhe expose
echo
echo "moving FP to BCV 950 "
sami FP moveabs 950
sleep 1
echo
echo "moving FP to channel 14: BCV=947"
sami FP moveabs 947
set sweepid = C014
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 14)"
sami dhe expose
echo
echo "moving FP to BCV 944 "
sami FP moveabs 944
sleep 1
echo
echo "moving FP to channel 15: BCV=941"
sami FP moveabs 941
set sweepid = C015
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 15)"
sami dhe expose
echo
echo "moving FP to BCV 938 "
sami FP moveabs 938
sleep 1
echo
echo "moving FP to channel 16: BCV=935"
sami FP moveabs 935
set sweepid = C016
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 16)"
sami dhe expose
echo
echo "moving FP to BCV 932 "
sami FP moveabs 932
sleep 1
echo
echo "moving FP to channel 17: BCV=929"
sami FP moveabs 929
set sweepid = C017
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 17)"
sami dhe expose
echo
echo "moving FP to BCV 926 "
sami FP moveabs 926
sleep 1
echo
echo "moving FP to channel 18: BCV=924"
sami FP moveabs 924
set sweepid = C018
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 18)"
sami dhe expose
echo
echo "moving FP to BCV 921 "
sami FP moveabs 921
sleep 1
echo
echo "moving FP to channel 19: BCV=918"
sami FP moveabs 918
set sweepid = C019
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 19)"
sami dhe expose
echo
echo "moving FP to BCV 915 "
sami FP moveabs 915
sleep 1
echo
echo "moving FP to channel 20: BCV=912"
sami FP moveabs 912
set sweepid = C020
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 20)"
sami dhe expose
echo
echo "moving FP to BCV 909 "
sami FP moveabs 909
sleep 1
echo
echo "moving FP to channel 21: BCV=906"
sami FP moveabs 906
set sweepid = C021
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 21)"
sami dhe expose
echo
echo "moving FP to BCV 903 "
sami FP moveabs 903
sleep 1
echo
echo "moving FP to channel 22: BCV=900"
sami FP moveabs 900
set sweepid = C022
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 22)"
sami dhe expose
echo
echo "moving FP to BCV 897 "
sami FP moveabs 897
sleep 1
echo
echo "moving FP to channel 23: BCV=894"
sami FP moveabs 894
set sweepid = C023
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 23)"
sami dhe expose
echo
echo "moving FP to BCV 891 "
sami FP moveabs 891
sleep 1
echo
echo "moving FP to channel 24: BCV=888"
sami FP moveabs 888
set sweepid = C024
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 24)"
sami dhe expose
echo
echo "moving FP to BCV 885 "
sami FP moveabs 885
sleep 1
echo
echo "moving FP to channel 25: BCV=882"
sami FP moveabs 882
set sweepid = C025
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 25)"
sami dhe expose
echo
echo "moving FP to BCV 879 "
sami FP moveabs 879
sleep 1
echo
echo "moving FP to channel 26: BCV=876"
sami FP moveabs 876
set sweepid = C026
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 26)"
sami dhe expose
echo
echo "moving FP to BCV 873 "
sami FP moveabs 873
sleep 1
echo
echo "moving FP to channel 27: BCV=870"
sami FP moveabs 870
set sweepid = C027
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 27)"
sami dhe expose
echo
echo "moving FP to BCV 867 "
sami FP moveabs 867
sleep 1
echo
echo "moving FP to channel 28: BCV=864"
sami FP moveabs 864
set sweepid = C028
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 28)"
sami dhe expose
echo
echo "moving FP to BCV 861 "
sami FP moveabs 861
sleep 1
echo
echo "moving FP to channel 29: BCV=859"
sami FP moveabs 859
set sweepid = C029
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 29)"
sami dhe expose
echo
echo "moving FP to BCV 856 "
sami FP moveabs 856
sleep 1
echo
echo "moving FP to channel 30: BCV=853"
sami FP moveabs 853
set sweepid = C030
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 30)"
sami dhe expose
echo
echo "moving FP to BCV 850 "
sami FP moveabs 850
sleep 1
echo
echo "moving FP to channel 31: BCV=847"
sami FP moveabs 847
set sweepid = C031
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 31)"
sami dhe expose
echo
echo "moving FP to BCV 844 "
sami FP moveabs 844
sleep 1
echo
echo "moving FP to channel 32: BCV=841"
sami FP moveabs 841
set sweepid = C032
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 32)"
sami dhe expose
echo
echo "moving FP to BCV 838 "
sami FP moveabs 838
sleep 1
echo
echo "moving FP to channel 33: BCV=835"
sami FP moveabs 835
set sweepid = C033
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 33)"
sami dhe expose
echo
echo "moving FP to BCV 832 "
sami FP moveabs 832
sleep 1
echo
echo "moving FP to channel 34: BCV=829"
sami FP moveabs 829
set sweepid = C034
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 34)"
sami dhe expose
echo
echo "moving FP to BCV 826 "
sami FP moveabs 826
sleep 1
echo
echo "moving FP to channel 35: BCV=823"
sami FP moveabs 823
set sweepid = C035
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 35)"
sami dhe expose
echo
echo "moving FP to BCV 820 "
sami FP moveabs 820
sleep 1
echo
echo "moving FP to channel 36: BCV=817"
sami FP moveabs 817
set sweepid = C036
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 36)"
sami dhe expose
echo
echo "moving FP to BCV 814 "
sami FP moveabs 814
sleep 1
echo
echo "moving FP to channel 37: BCV=811"
sami FP moveabs 811
set sweepid = C037
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 37)"
sami dhe expose
echo
echo "moving FP to BCV 808 "
sami FP moveabs 808
sleep 1
echo
echo "moving FP to channel 38: BCV=805"
sami FP moveabs 805
set sweepid = C038
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 38)"
sami dhe expose
echo
echo "moving FP to BCV 802 "
sami FP moveabs 802
sleep 1
echo
echo "moving FP to channel 39: BCV=799"
sami FP moveabs 799
set sweepid = C039
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 39)"
sami dhe expose
echo
echo "moving FP to BCV 796 "
sami FP moveabs 796
sleep 1
echo
echo "moving FP to channel 40: BCV=794"
sami FP moveabs 794
set sweepid = C040
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 40)"
sami dhe expose
echo
echo "moving FP to BCV 791 "
sami FP moveabs 791
sleep 1
echo
echo "moving FP to channel 41: BCV=788"
sami FP moveabs 788
set sweepid = C041
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 41)"
sami dhe expose
echo
echo "moving FP to BCV 785 "
sami FP moveabs 785
sleep 1
echo
echo "moving FP to channel 42: BCV=782"
sami FP moveabs 782
set sweepid = C042
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 42)"
sami dhe expose
echo
echo "moving FP to BCV 779 "
sami FP moveabs 779
sleep 1
echo
echo "moving FP to channel 43: BCV=776"
sami FP moveabs 776
set sweepid = C043
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 43)"
sami dhe expose
echo
echo "moving FP to BCV 773 "
sami FP moveabs 773
sleep 1
echo
echo "moving FP to channel 44: BCV=770"
sami FP moveabs 770
set sweepid = C044
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 44)"
sami dhe expose
echo
echo "moving FP to BCV 767 "
sami FP moveabs 767
sleep 1
echo
echo "moving FP to channel 45: BCV=764"
sami FP moveabs 764
set sweepid = C045
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 45)"
sami dhe expose
echo
echo "moving FP to BCV 761 "
sami FP moveabs 761
sleep 1
echo
echo "moving FP to channel 46: BCV=758"
sami FP moveabs 758
set sweepid = C046
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 46)"
sami dhe expose
echo
echo "moving FP to BCV 755 "
sami FP moveabs 755
sleep 1
echo
echo "moving FP to channel 47: BCV=752"
sami FP moveabs 752
set sweepid = C047
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 47)"
sami dhe expose
echo
echo "moving FP to BCV 749 "
sami FP moveabs 749
sleep 1
echo
echo "moving FP to channel 48: BCV=746"
sami FP moveabs 746
set sweepid = C048
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 48)"
sami dhe expose
echo
echo "moving FP to BCV 743 "
sami FP moveabs 743
sleep 1
echo
echo "moving FP to channel 49: BCV=740"
sami FP moveabs 740
set sweepid = C049
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 49)"
sami dhe expose
echo
echo "moving FP to BCV 737 "
sami FP moveabs 737
sleep 1
echo
echo "moving FP to channel 50: BCV=734"
sami FP moveabs 734
set sweepid = C050
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 50)"
sami dhe expose
echo
echo "moving FP to BCV 731 "
sami FP moveabs 731
sleep 1
echo
echo "moving FP to channel 51: BCV=729"
sami FP moveabs 729
set sweepid = C051
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 51)"
sami dhe expose
echo
echo "moving FP to BCV 726 "
sami FP moveabs 726
sleep 1
echo
echo "moving FP to channel 52: BCV=723"
sami FP moveabs 723
set sweepid = C052
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 52)"
sami dhe expose
echo
echo "moving FP to BCV 720 "
sami FP moveabs 720
sleep 1
echo
echo "moving FP to channel 53: BCV=717"
sami FP moveabs 717
set sweepid = C053
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 53)"
sami dhe expose
echo
echo "moving FP to BCV 714 "
sami FP moveabs 714
sleep 1
echo
echo "moving FP to channel 54: BCV=711"
sami FP moveabs 711
set sweepid = C054
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 54)"
sami dhe expose
echo
echo "moving FP to BCV 708 "
sami FP moveabs 708
sleep 1
echo
echo "moving FP to channel 55: BCV=705"
sami FP moveabs 705
set sweepid = C055
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 55)"
sami dhe expose
echo
echo "moving FP to BCV 702 "
sami FP moveabs 702
sleep 1
echo
echo "moving FP to channel 56: BCV=699"
sami FP moveabs 699
set sweepid = C056
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 56)"
sami dhe expose
echo
echo "moving FP to BCV 696 "
sami FP moveabs 696
sleep 1
echo
echo "moving FP to channel 57: BCV=693"
sami FP moveabs 693
set sweepid = C057
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 57)"
sami dhe expose
echo
echo "moving FP to BCV 690 "
sami FP moveabs 690
sleep 1
echo
echo "moving FP to channel 58: BCV=687"
sami FP moveabs 687
set sweepid = C058
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 58)"
sami dhe expose
echo
echo "moving FP to BCV 684 "
sami FP moveabs 684
sleep 1
echo
echo "moving FP to channel 59: BCV=681"
sami FP moveabs 681
set sweepid = C059
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 59)"
sami dhe expose
echo
echo "moving FP to BCV 678 "
sami FP moveabs 678
sleep 1
echo
echo "moving FP to channel 60: BCV=675"
sami FP moveabs 675
set sweepid = C060
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 60)"
sami dhe expose
echo
echo "moving FP to BCV 672 "
sami FP moveabs 672
sleep 1
echo
echo "moving FP to channel 61: BCV=669"
sami FP moveabs 669
set sweepid = C061
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 61)"
sami dhe expose
echo
echo "moving FP to BCV 666 "
sami FP moveabs 666
sleep 1
echo
echo "moving FP to channel 62: BCV=664"
sami FP moveabs 664
set sweepid = C062
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 62)"
sami dhe expose
echo
echo "moving FP to BCV 661 "
sami FP moveabs 661
sleep 1
echo
echo "moving FP to channel 63: BCV=658"
sami FP moveabs 658
set sweepid = C063
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 63)"
sami dhe expose
echo
echo "moving FP to BCV 655 "
sami FP moveabs 655
sleep 1
echo
echo "moving FP to channel 64: BCV=652"
sami FP moveabs 652
set sweepid = C064
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 64)"
sami dhe expose
echo
echo "moving FP to BCV 649 "
sami FP moveabs 649
sleep 1
echo
echo "moving FP to channel 65: BCV=646"
sami FP moveabs 646
set sweepid = C065
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 65)"
sami dhe expose
echo
echo "moving FP to BCV 643 "
sami FP moveabs 643
sleep 1
echo
echo "moving FP to channel 66: BCV=640"
sami FP moveabs 640
set sweepid = C066
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 66)"
sami dhe expose
echo
echo "moving FP to BCV 637 "
sami FP moveabs 637
sleep 1
echo
echo "moving FP to channel 67: BCV=634"
sami FP moveabs 634
set sweepid = C067
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 67)"
sami dhe expose
echo
echo "moving FP to BCV 631 "
sami FP moveabs 631
sleep 1
echo
echo "moving FP to channel 68: BCV=628"
sami FP moveabs 628
set sweepid = C068
set cmd = `sami dhe dbs set $sweepkey $sweepid`
sami dhe set image.basename $basename"_"$sweepid
echo "SWEEP $sweepid"
echo "taking data...(sweep $sweepid step 68)"
sami dhe expose
# Channel: +Step ==> BCV
# [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68]
# [0, -6, -6, -6, -6, -6, -5, -6, -6, -6, -6, -6, -6, -6, -6, -6, -6, -5, -6, -6, -6, -6, -6, -6, -6, -6, -6, -6, -5, -6, -6, -6, -6, -6, -6, -6, -6, -6, -6, -5, -6, -6, -6, -6, -6, -6, -6, -6, -6, -6, -5, -6, -6, -6, -6, -6, -6, -6, -6, -6, -6, -5, -6, -6, -6, -6, -6, -6]
# [1024, 1018, 1012, 1006, 1000, 994, 989, 983, 977, 971, 965, 959, 953, 947, 941, 935, 929, 924, 918, 912, 906, 900, 894, 888, 882, 876, 870, 864, 859, 853, 847, 841, 835, 829, 823, 817, 811, 805, 799, 794, 788, 782, 776, 770, 764, 758, 752, 746, 740, 734, 729, 723, 717, 711, 705, 699, 693, 687, 681, 675, 669, 664, 658, 652, 646, 640, 634, 628]
