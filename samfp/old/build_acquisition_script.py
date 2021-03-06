#!/usr/bin/env python

import scipy.constants as const
import time
import os
import sys

"""

    THIS PROGRAM COMPUTE A SCANNING SEQUENCE FOR PF/SAM/SOAR
    Philippe Amram
    previous update: 2015, March, 19
    last update: 2016, September, 30


NOTATIONS:
    epais = distance between the two plates
    gap = the maximum tuning gap
    QGC = Queensgate Constant
    BCV = Binary Control Value

    INTERACTIVE
    In interactive mode, interactive = True, in non-interactive mode, interactive = False
"""

# Script Configuration --------------------------------------------------------
interactive = False

# Choose 1 for the Low-Resolution FP p = 134
# or 2 for the High-Resolution FP p = 609.
# Only for non-interactive mode.
which_fp = 2

# Free Spectral Range in BCV units
free_spectral_range_bcv = 360.

# Source gas
source = 'Ne'



# Main Function ---------------------------------------------------------------
def main():

    global lamb, gap_size
    print(
        "\n{}".format("-" * 100) +
        "\n WELCOME ! " +
        "{}".format(time.strftime('%a, %d %b %Y %H:%M:%S GMT')) +
        "\n     This program prepares your script to run on FP/SAMI"
    )

    # CONSTANTS --------------------------------------------------------------

    light_speed = const.physical_constants["speed of light in vacuum"][0]
    light_speed /= 1000 # convert from m/s to km/s

    wavelength = {
        'Ha': 6562.78,
        'SIIf': 6716.47,
        'SIIF': 6730.85,
        'NIIf': 6548.03,
        'NIIF': 6583.41,
        'Ne': 6598.9529
    }

    bcv_max = 4095    # 4096 value starting from 0 up to 4095

    # INITIALISATION OF THE TWO SCRIPT FILES ---------------------------------
    # 1) INITIALISATION OF THE SCANNING SCRIPT
    tt = time.strftime('%Y-%m-%dT%Hh%Mm%Ss')

    # 2) INITIALISATION OF THE RUNNING DIRECTORY

    #dirtime = time.strftime('%Y%m%d')
    dirtime = "20170301"
    if interactive:
        print("\n Data of the observing run. ")
        print(" The date of the run (e.g. 20150130) will be automatically added to the address of the directory you will give now")
        sdir = input(" Please, input the directory name (e.g.:/home2/images/): ")
        # sdir = '/home2/images/'
        print("     Your input is: {}".format(sdir))
        print("     The data of the day will go into the directory : ",sdir + dirtime + '/')
        running = input("\n Give the running directory name where you will put and run the script (e.g. 001): ")
        sdir = sdir + dirtime + "/" + running
        print("     The name of the directory where the script will be ran is : ",sdir)
    else:
        print(dirtime)
        running = input("\n Give the running directory name where you will put and run the script (e.g. 001): ")
        if type(running) in [int, float]:
            running = "{:03d}".format(running)

        sdir = os.path.join("/home2/images/SAMFP/", dirtime, running)

    """ 3) SCRIPT TO RUN TO COPY THE SCANNING SCRIPT FROM MY COMPUTER TO BTFI COMPUTER """

    tt = running
    ttsh = tt+'.sh'
    Fichier = open(ttsh,'w')
    Fichier.write("#!/bin/csh -f\n\n")
    Fichier0 = open('scpbtfidr.sh','w')
    Fichier0.write("#!/bin/csh -f\n\n")
    #    Fichier0.write("sshpass -p \"btfi88\" scp {} btfidr@139.229.18.227:/data/{}/{}/\n".format(ttsh,dirtime,running))
    Fichier0.write("sshpass -p \"btfi88\" scp {} btfidr@139.229.18.227:/data/{}/scripts/\n".format(ttsh,dirtime))
    # btfidr@btfidr:/home2/images/20150317
    Fichier0.close()

    """
    
FABRY-PEROT TO USE
    
    """

    dico0 = {}
    dico0[1,1] = "Thickness =  44 microns; tunable gap = 2 microns; p=134 @ Halpha"
    dico0[1,2] = "Thickness = 200 microns; tunable gap = 2 microns; p=609 @ Halpha"

    if interactive:
        print("\n Please, input the name of the Fabry-Perot you wanted to use: ")
        print("      For TF ({}) put (1) ".format(dico0[1,1]))
        print("      For PF ({}) put (2) ".format(dico0[1,2]))
        pftf = int(input(" Your choice : "))

    else:
        pftf = which_fp

    if pftf > 2:
        print("      Sorry, you input a value not allowed, choose between (1) and (2), please restart ")
        sys.exit(0)
    else:
        if pftf == 1:
            print("     Your input is : {}".format(dico0[1,1]))
        if pftf == 2:
            print("     Your input is : {}".format(dico0[1,2]))

#epais = float(input(" Please, input the thickness (not the gap) of the interferometer in $mu m$ (it should be a float, eg epais=350): "))
#epais = p_order * lamb*1e-4 /2

    if pftf == 1:
        gap_size = 44.
        
    elif pftf == 2:
        gap_size = 200.


    """
    
CALIBRATION OR OBSERVATION
    
    """

    if interactive:
        calibration = int(input("\n Please, input if you make a calibration (0) or an observation (1): "))

        if calibration == 0:
            lamb = wavelength['Ne']
            print("     The wavelength of the Neon line will be: {:g}".format(lamb))
    else:
        calibration = int(input("\n Please, input if you make a calibration (0) or an observation (1): "))

    if calibration > 1:
        print("      Sorry, you input a value not allowed, choose between (1) and (2), please restart ")
        sys.exit(0)
                              
    if interactive:

        if calibration == 0:
            print("     You requested a calibration.")
            lamb = wavelength['Ne']

        else:
            print(
                "\n You resqueted an observation."
                "\n You have to give the wavelength at rest of the line you will observe."
            )
            temp = input("\n > ")
            lamb = float(temp)

    else:

        if calibration == 0:
            lamb = wavelength['Ne']

        else:
            lamb = wavelength[source]

    if lamb < 0:
        print("      Sorry, you input a value not allowed because {} should be greater than 0, please restart ".format(lamb))
        sys.exit(0)

    lamb_rest=lamb

    if calibration == 0:
        vitesse = 0 # km/s

    if calibration == 1:
        if interactive:
            object_name = input("\n Please, input the name of your object (e.g. NGC 7331): ")
            print("     Your input is: {} ".format(object_name))
            vitesse = float(input("\n Please, input the radial velocity of the galaxy (in km/s): "))
            print("     Your input is: {} km/s".format(vitesse))
        else:
            object_name = input("\n Please, input the name of your object (e.g. NGC 7331): ")
            print("     Your input is: {} ".format(object_name))
            vitesse = float(input("\n Please, input the radial velocity of the galaxy (in km/s): "))
            print("     Your input is: {} km/s".format(vitesse))

    """
    
INITIAL PARAMETER COMPUTATION
    
    """

    def ISL(ll,pp):
        #fsr_lamb = lamb/p_order
        isl_ll  = ll/pp*(1+1/(pp*pp))
        return isl_ll
    
    def P_ORDER(ee,ll):
        porder = 2. * ee * 1E+4 / ll
        return porder
        
    lamb = (vitesse / light_speed + 1) * lamb_rest

    p_order = P_ORDER(gap_size, lamb)
    p_order_halpha = P_ORDER(gap_size, wavelength['Ha'])
    p_order_Ne = P_ORDER(gap_size, wavelength['Ne'])

    p_order0 = int(p_order)
    e_fsr = gap_size /p_order

    fsr_lamb = ISL(lamb,p_order)
    fsr_lamb_Ne = ISL(wavelength['Ne'], p_order_Ne)
    fsr_lamb_Ha = ISL(wavelength['Ha'], p_order_halpha)

    fsr_kms = light_speed * fsr_lamb / lamb

    Fichier.write("# General parameters:\n")
    Fichier.write("#      - You requested to use the following FP: {} \n".format(dico0[1,pftf]))
    if calibration == 0 :
        Fichier.write("#      - You requested to do a CALIBRATION (and not an observation on the sky)\n")
    if calibration == 1 :
        Fichier.write("#      - You requested to do a OBSERVATION (and not a calibration)\n")
        Fichier.write("#      - The name of the object                         : {}\n".format(object_name))
    Fichier.write("#      - The wavelength (at rest) you gave is             = {:g} angstroms\n".format(lamb_rest))
    if calibration == 1 :
        Fichier.write("#      - The radial velocity is                           = {:g} km/s\n".format(vitesse))
    if calibration == 1 :
        Fichier.write("#      - The wavelength (redshifted)                      = {:g} angstroms\n".format(lamb))
    Fichier.write("# Interference order:\n")
    Fichier.write("#      - The interference order @ {:g}                 = {:g} \n".format(wavelength['Ha'],p_order_halpha))
    Fichier.write("#      - The interference order @ {:g}                 = {:g} \n".format(wavelength['Ne'],p_order_Ne))
    Fichier.write("#      - The interference order @ {:g}                 = {:g} \n".format(lamb,p_order))
    Fichier.write("# Free Spectral Range :\n")
    Fichier.write("#      - The FSR @ {:g} in wavelength                  = {:g} Angstrom\n".format(wavelength['Ne'],fsr_lamb_Ne))
    Fichier.write("#      - The FSR @ {:g} in wavelength                  = {:g} Angstrom\n".format(wavelength['Ha'],fsr_lamb_Ha))
    Fichier.write("#      - The FSR @ {:g} in thickness                   = {:g} microns \n".format(lamb,e_fsr))
    Fichier.write("#      - The FSR @ {:g} in wavelength                  = {:g} Angstrom\n".format(lamb,fsr_lamb))
    Fichier.write("#      - The FSR @ {:g} in km/s                        = {:g} km/s\n".format(lamb,fsr_kms))

    """
    
QUEENSGATE CONSTANT
    
    """

    if interactive:
        print("\n (1) If you know it, you can use the Queensgate Constant already measured with the SAME CS100 AND the the SAME FP.")
        print(" (2) If you do not know, you must put the total plate gap in BCV corresponding to one FSR at the wavelength")
        print("     '1' means you DO     want to give a the Queensgate Constant.")
        print("     '2' means you DO NOT want to give a the Queensgate Constant but a number of BCV corresponding to one FSR")
        QGC_or_not = int(input(" your input ('1' or '2'): "))
    else:
        QGC_or_not = 2

    if QGC_or_not > 2 or QGC_or_not < 1:
        print("      Sorry, you input {} which is a value not allowed please choose '1' or '2' ".format(QG_or_not))
        sys.exit(0)

    if QGC_or_not == 1:
        if interactive:
            QGC = float(input("\n Please, input the Queensgate Constant (in Angstrom, could be a float, e.g. 9.30): "))
            #QGC = 9.15
            print("     Your input is: {} Angstroms.".format(QGC))
        else:
            QGC = 9.15  # undersampling
            QGC = 9.40  # oversampling
            QGC = 9.30  # close to be perfect

#dico0[1,1] = "Thickness =  44 microns; tunable gap = 2 microns; p=134 @ Halpha"
#dico0[1,2] = "Thickness = 200 microns; tunable gap = 2 microns; p=609 @ Halpha"

    """ 4096 BCV values are available with the CS100, ranging from -2047 to +2048, thus for both interferometer which have a tunable gap of 2 microns, 1 BCV should be equal to 2 microns/4096 = 0.49 nm = 4.9 A.
        On the other hand, by definition, QCG = 2 * 1 BCV = 9.8 A/BCV
        Obviously  fsr_bcv_lamb_QGC = lambda / Q
                                    = 6563 / 9.8 
                                    = 670 BCV 
        but we in fact measure half of it = 335 BCV, this could be due to a bit which is not working any more and so, one BCV is indeed 2 BCV...
    """
    
    if QGC_or_not == 2:
        if interactive:
            print("\n You first must choose the wavelength at which the gap in BCV will be given.")
            print(" NOTE: this value is not necessary the scanning wavelength.")
            # lamb_QGC = float(input(" Give this wavelength (could be a float e.g. Ne 6598.9529): "))
            lamb_QGC = 6598.9529
            print("\n Please, input the total plate gap in BCV corresponding to one FSR at the wavelength {} of reference".format(lamb_QGC))
            print(" The BCV range between 0 and {}".format(bcv_max))
            fsr_bcv_lamb_QGC = float(input(" your input (could be a float, e.g. 705): "))
            #fsr_bcv_lamb_QGC = 352.75
            print("     Your input is: {}".format(fsr_bcv_lamb_QGC))
        else:
            fsr_bcv_lamb_QGC = free_spectral_range_bcv
            lamb_QGC = wavelength['Ne']
        QGC = lamb_QGC / fsr_bcv_lamb_QGC
        print("     A queensgate has been computed : {}".format(QGC))

    fsr_bcv_lamb    = lamb / QGC
    fsr_bcv_lamb_Ha = wavelength['Ha'] / QGC
    fsr_bcv_lamb_Ne = wavelength['Ne'] / QGC

    """
    
NUMBER OF CHANNELS TO SCAN
    
    """

    if interactive:
        print("\n Taking into account the Finesse and the sampling, the number of channel to scan could be computed automatically.")
        print(" Alternatively you can define yourself the number of channels to scan.")
        print("     (1) You DO WISH to compute automatically the number of channels to scan")
        print("     (2) You DO NOT WISH to give manually the number of channels to scan")
        nchan_manuel = int(input("          Please give you choose (1 or 2): "))
    else:
        nchan_manuel = 1

    if nchan_manuel == 1:
        if interactive:
            finesse = float(input("\n Please, input the Finesse (finesse must be a float): "))
        else:
            finesse = 17.75
            finesse = 30.46
#            finesse = 20.8
        if finesse <= 1:
            print("      Sorry, you input a value not allowed because {:g} should be greater than 1, please restart ".format(finesse))
            sys.exit(0)
        if interactive:
            sampling = float(input("\n Please, input the sampling, Shannon indicates that the sampling could be 2 (could be a float): "))
        else:
            sampling = 2.0
        if sampling <= 1:
            print("      Sorry, you input a value not allowed because {:g} should be greater or equal to one, please restart ".format(sampling))
            sys.exit(0)
        """ Integer value + 1 to avoid undersampling """
        nchan = sampling*finesse

    if nchan_manuel == 2:
        if interactive:
            nchan = int(input("\n Please input the number of channel to scan one FSR (must be an integer): "))
        else:
            nchan = 38

    bcv_step = fsr_bcv_lamb / nchan
    if bcv_step < 2:
        print("\n     Sorry, your scanning step in BCV ={:g} is too small, it should not be lower than 2.".format(bcv_step))
        if nchan_manuel == 1:
            print("     This could be due to the finesse (={:g}) or/and the sampling (={:g}) too high.".format(finesse,sampling))
        if nchan_manuel == 2:
            print("     This could be due to the number of channels (={:g}) too high.".format(nchan))
        print("     Please RESTART from the beginning.")
        sys.exit(0)

    Fichier.write("#      - The queensgate constant QGC                      = {:g} Angstrom\n".format(QGC))
    Fichier.write("#      - The FSR in BCV @ {:g}A                        = {:g}\n".format(lamb,fsr_bcv_lamb))
    Fichier.write("#      - The FSR in BCV @ {:g}A                        = {:g}\n".format(wavelength['Ha'],fsr_bcv_lamb_Ha))
    Fichier.write("#      - The FSR in BCV @ {:g}A                        = {:g}\n".format(wavelength['Ne'],fsr_bcv_lamb_Ne))
    Fichier.write("# Finesse & Scanning:\n")
    if nchan_manuel == 1:
        Fichier.write("#      - You gave a real finesse                         = {:g}\n".format(finesse))
        Fichier.write("#      - Shannon sampling of the finesse                 = {:g}\n".format(sampling))
        Fichier.write("#      - Considering F={:g} and the sampling ={:g}, the float nb of ch to scan for one FSR  = {:g}\n".format(finesse,sampling,nchan))
        Fichier.write("#      - Considering F={:g} and FSR={:g}, the spectral sampling = {:g} Angstroms\n".format(finesse,fsr_lamb,fsr_lamb/finesse))
        Fichier.write("#      - The spectral Resolution @ {:g} Angstroms        = {:g}\n".format(lamb,int(lamb*finesse/fsr_lamb)))
    else:
        Fichier.write("#      - The number of channels to scan for one FSR      = {:g}\n".format(nchan))
    Fichier.write("#      - The average number of BCV for one FSR             = {:g}\n".format(bcv_step))

    """ For technical reasons I added the parameter delta_iBCV_max (29/09/2016), it seems indeed that the f. CS100 does not respect the order when we resquest to jump a large BCV range at once, thus I introduced a pause of 1 second (sleep 1) each time it moves delta_iBCV_max BCV """
        
    delta_iBCV_max=3
    Fichier.write("#      - The maximum number of BCV that the CS100 can jump at once = {:g}\n".format(delta_iBCV_max))
    
    """
    
SCAN MORE THAN ONE FSR ?
    
    """

    if interactive:
        print("\n You can scan more than one FSR.")
        print(" NOTE: The number of channel to scan for more than one FSR will be larger and computed automatically.")
        overlap = float(input(" Please, input the number of FSR you want to scan (could be a float, \"1\" means you will scan one FSR): "))
    else:
        overlap = 1.1

    if overlap < 0:
        print("      Sorry, you input a value not allowed because {:g} should be greater than 0, please restart ".format(overlap))
        sys.exit(0)

    if (fsr_bcv_lamb*overlap) > bcv_max:
        print(
            "\n Sorry, you input a value not allowed because "
            "{:d} X {:d} = {:d} is greater than {:d}.".format(
                int(fsr_bcv_lamb, overlap), int(fsr_bcv_lamb * overlap), bcv_max
                ) +
              "\n Please RESTART from the beginning.")
        sys.exit(0)
    else:
        fsr_bcv_lamb *= overlap
        nchan = int(nchan * overlap)+1

    Fichier.write("# Overscanning:\n")
    Fichier.write("#      - You wanted to scan                                 = {:g} FSR \n".format(overlap))
    Fichier.write("#      - The BCV gap that will be scanned @ {:g} Angstro = {:g}\n".format(lamb,fsr_bcv_lamb))
    Fichier.write("#      - The total number of channels that will be scanned  = {:g}\n".format(nchan))

    """ TO SCAN IN DECREASING  THE RADIUS OF THE RINGS """
    #nfiniz0 = int(input(" Please, input the zero Z value (nfiniz0 must be an integer): "))
    #input(" Please, input the initial Z value (nfiniz must be an integer): "))
    #nfiniz0 =  0
    #       DIVIDED BY 4 BECAUSE OF THE UNAVAILABLE BCV RANGE
    #nfiniz0 =  int(bcv_max/4)
    #nfiniz = nfiniz0 - int(fsr_bcv_lamb/4.)

    """ TO SCAN IN INCREASING  THE RADIUS OF THE RINGS """
    #nfiniz0 =  int(bcv_max/4)
    #nfiniz = nfiniz0 + int(fsr_bcv_lamb/4.)
    nfiniz = 1024
    nfiniz_end = nfiniz - (nchan - 1) * bcv_step

    """ Checking using the basic formula """
    base = lamb / QGC
    step = base / nchan
    # print("lamb= ",lamb," QGC =",QGC," nchan =",nchan," base (BCV)= ",base," step (BCV)= ",step)

    #Fichier.write("#      - The zero BCV value     (nfiniz0)                   = {:g}\n".format(nfiniz0))
    Fichier.write("#      - The initial BCV value   (nfiniz)                   = {:g}\n".format(nfiniz))
    Fichier.write("#      - The final BCV value should be around (nfiniz_end)  = {:g}\n".format(nfiniz_end))
    
    uneminute = 60. # second
    if calibration == 0:
        basename = "p609_cal"
    if calibration == 1:
        basename = "p609_obs"
    if interactive:
        #nsweeps    = int(input(" Please, input how many \"sweeps\" will be done on this scan (nsweeps must be an integer): "))
        nsweeps     = 1
        #nsteps     = int(input(" Please, input how many Z steps each sweep will have (nsteps must be an integer): "))
        nsteps      = 1
        #nframe     = int(input(" Please, input how many images we will take in each step (each Z value, nframe must be an integer): "))
        nframe      = 1
        basename    = input("\n Please, set the basename of your fits image (basename must be a string, e.g. fp_sami): ")
        #basename = "fp_sami"
        print("     Your basename is : ",basename)
        #binxy       = input("\n Please, set the binning of the CCD image (binxy must be an integer, e.g. 4 for a 4x4 binning): ")
        binxy = 4
        exptim      = float(input("\n Please, set the image exposure time per channel in seconds (exptim could be a float): "))
        #exptim = 5
    else:
        nsweeps = 1
        binxy = 4
        nsteps = 1
        nframe = 1
        #basename = "fp_sami"
        exptim_min = 5
        exptim = exptim_min * uneminute
        exptim      = float(input("\n Please, set the image exposure time per channel in seconds (exptim could be a float): "))
        #exptim = 120.

    readout_time = 3.        # 3 seconds = readout time @ binxy = 4 x 4 ???
    exptim_total = (nchan * (exptim + readout_time)) / uneminute

    if exptim < 0:
        print("      Sorry, you input a value not allowed because {:g} should be greater than 0, please restart ".format(exptim))
        sys.exit(0)

    Fichier.write("# SAMI:\n")
    Fichier.write("#      - You gave nsweeps  = {}\n".format(nsweeps))
    Fichier.write("#      - You gave nsteps   = {}\n".format(nsteps))
    Fichier.write("#      - You gave nframe   = {}\n".format(nframe))
    Fichier.write("#      - You gave exptim per channel             = {:g} seconds\n".format(exptim))
    Fichier.write("#      - Readout time per exposure               = {:g} seconds \n".format(readout_time))
    Fichier.write("#      - Total exposure time (whole observation) = {:g} minutes\n".format(exptim_total))
    Fichier.write("#      - Total exposure time (whole observation) = {:g} hours\n".format(exptim_total/uneminute))
    Fichier.write("#      - You gave binxy                          = {} \n".format(binxy))
    Fichier.write("#      - You gave the basename                   = {}\n\n".format(basename))
    Fichier.write("set dat = `date +%Y-%m-%dT%H:%M:%S`\n")
    Fichier.write("set scid = \"SCAN_$dat\"\n")
    Fichier.write("echo \"SCAN $scid\"\n")
    Fichier.write("set sweepkey = \"FAPERSWP\"\n")
    Fichier.write("set stepkey = \"FAPERSST\"\n")
    Fichier.write("set scankey = \"FAPERSID\"\n")
    Fichier.write("set nsweeps = {}\n".format(nsweeps))
    Fichier.write("set nsteps = {}\n".format(nsteps))
    Fichier.write("set nframe = {}\n".format(nframe))
    Fichier.write("set nfiniz = {}\n".format(nfiniz))
    Fichier.write("set exptim = {}\n".format(exptim))
    Fichier.write("set binxy = {}\n".format(binxy))
    #Fichier.write("set basename = \"fp_sami\"\n")
    Fichier.write("set basename = \"{}\"\n".format(basename))
    Fichier.write("set cmd = `sami dhe set image.dir {}`\n".format(sdir))
    Fichier.write("set cmd = `sami dhe dbs set $scankey $scid`\n")
    Fichier.write("set cmd = `sami dhe dbs set $stepkey custom`\n")
    Fichier.write("echo \"setting number of images, exposure time and basename\"\n")
    Fichier.write("sami dhe set binning $binxy $binxy\n")
    Fichier.write("sami dhe set obs.nimages $nframe\n")
    Fichier.write("sami dhe set obs.exptime $exptim\n")
    Fichier.write("sami dhe set image.basename $basename\n")
    Fichier.write("echo\n")
    Fichier.write("echo \"image $basename, exptime $exptim\"\n")
    Fichier.write("echo \"binning $binxy\"\n")

    dico = {'channel':[], 'step':[], 'BCV':[]}
    iBCV = 0
    delta_iBCV = 0
    ip = 1
    ipm = 1
    if ip <= ipm:
        for cnt in range(1,nchan+1,ip):
            ip += 1
            iBCV0 = iBCV
            BCV = nfiniz - (cnt-1) * bcv_step
            if BCV >= 0:
                if int(BCV + 0.5) > int(BCV):
                    iBCV = int(BCV)+1
                else:
                    iBCV = int(BCV)
            else:
                if int(BCV - 0.5) < int(BCV):
                    iBCV = int(BCV)-1
                else:
                    iBCV = int(BCV)
            #print("ip=",ip,"  cnt=",cnt," BCV=",BCV,"  iBCV=",iBCV)
            if cnt == 1 :
                delta_iBCV = 0
            else:
                delta_iBCV = iBCV-iBCV0
            delta_iBCV_temp=delta_iBCV
            icompt = 0
            while abs(delta_iBCV_temp) > delta_iBCV_max:
                #print("je suis dans la boucle",cnt)
                icompt += 1
                #print("delta_iBCV_temp=",delta_iBCV_temp,"  delta_iBCV_max=",delta_iBCV_max)
                Fichier.write("echo\n")
                itemp = iBCV0-icompt*delta_iBCV_max
                #print("iBCV=",iBCV)
                Fichier.write("echo \"moving FP to BCV {} \"\n".format(itemp))
                Fichier.write("sami FP moveabs {}\n".format(itemp))
                Fichier.write("sleep 1\n")
                delta_iBCV_temp += delta_iBCV_max
            Fichier.write("echo\n")
            Fichier.write("echo \"moving FP to channel {}: BCV={}\"\n".format(cnt,iBCV))
            Fichier.write("sami FP moveabs {}\n".format(iBCV))
            Fichier.write("set sweepid = C%03d\n"%cnt)
            Fichier.write("set cmd = `sami dhe dbs set $sweepkey $sweepid`\n")
            Fichier.write("sami dhe set image.basename $basename\"_\"$sweepid\n")
            Fichier.write("echo \"SWEEP $sweepid\"\n")
            Fichier.write("echo \"taking data...(sweep $sweepid step {})\"\n".format(cnt))
            Fichier.write("sami dhe expose\n")
            dico['channel'].append(cnt)
            dico['step'].append(delta_iBCV)
            dico['BCV'].append(iBCV)
        Fichier.write("# Channel: +Step ==> BCV\n")
        Fichier.write("# {}\n".format(dico['channel']))
        Fichier.write("# {}\n".format(dico['step']))
        Fichier.write("# {}\n".format(dico['BCV']))

    Fichier.close()

    print("\n     The name of the script you have to run on SAMI computer is : ",ttsh)
    print("     Copy the following script to SAMI computer in the following directory : ",sdir + '/')
    print("     NOTE: You have to pass by BTFIDR computer to have access to SAMI computer")
    print("     To copy the script from your computer to BTFI computer,")
    print("     run the script \"scpbtfidr.sh\" which have been created now.")
    print("\n END OF THE PROGRAM")
    print("{}".format("-"*100))

if __name__ == '__main__':
    main()

