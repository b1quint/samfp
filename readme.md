#SAM-FP

 This page contains some scripts that help me (and hopefully will
 help you too) to reduce Fabry-Perot data obtained at 
 [SOAR Telescope](http://www.ctio.noao.edu/soar/) with 
 [SOAR Adaptive Module](http://www.ctio.noao.edu/soar/content/soar-adaptive-optics-module-sam),
 or SAM. 

 This observing mode is considered a Restricted User Instrument and you 
 will have support to reduce, edit, visualize and manipulate your data.

 Scripts for data-reduction are saved inside the `scripts` folder. 
 Each script is explained bellow. The sequence that they are explained 
 is related to their use for a standard data-reduction process.
 
## fix_header.py
 
This script fixes the header of the images obtained with SAMI so they 
can be handled by `ccdproc.ImageFileCollection`. The fix involves 
simply removing the `ADC` card that appears twice in the header and 
causes the class above to raise errors. 

This script can be used by simply:
```
    $ python fix_header.py root_directory
```

The `-v`/`--verbose` option is available if you want to follow up the 
status of the script but it makes the process much slower.


## xjoin.py

Every single `.fits` file obtained with SAMI, SAM's Imager, has four 
extension. I find it much easier to work with files that contains a 
single extension so I created the `samfp_xjoin.py` script joins all the 
extensions and a lot of other things. 
 
This script will always:

  * Read each extension;
  * Read the overscan region for each extension based on information in the header;
  * Collapse (sum) the overscan region in the short axis; 
  * Fit a 3rd degree polynomium to the overscan region;
  * Subtract the fitted polynomium from every column of each extension;
  * Put all the extensions together in a single array;

After that, this script may also:

  * Simple BIAS subtraction;
  * Simple DARK subtraction;
  * Simple division by FLAT;
  * Simple division by the exposure time (EXPTIME);
  * Clean hot columns and lines;
  * Clean cosmic rays using [LACosmic](http://www.astro.yale.edu/dokkum/lacosmic/ "Visit LACosmic Webpage");
  * Remove the instrument fingerprint that sometimes shows up as glows in the lower lateral borders;
  * Add HISTORY card that stores all the steps taken with it.

This file can be executed in a common terminal by simply calling
``` 
  $ python samfp_xjoin.py [options] file1 file2 ... fileN
```  
  Or
```  
  $ chmod a+x samfp_xjoin.py
  $ ./samfp_xjoin.py [options] file1 file2 ... fileN
```

The options can be printed if one executes
```
  $ python samfp_xjoin.py --help
```
  or
```
  $ python sami_xjoin.py -h
```

 ## samfp_imcombine.py
    
 This script combines 2D images that are used as standard calibrations. 

 ## mkcube.py
 
 
 
 ## phmxtractor.py
 
  When we observe with a Fabry-Perot, we take several images while changing 
  the gap size between the two FP plates. This process is called _scanning_ or 
  a _scan_. For each gap size, the information (light) related to a single 
  wavelength lies on a ring. As we increase the gap size, this ring increases
  in radius.
  
  When we stack all the images obtained in a scan, the information related
  to a given wavelength lies on a parabolic surface along the data-cube. At 
  this point, we need to shift each pixel's spectrum to align this information
  so all the light at a given wavelength lies in a single frame. 
  
  For that, we use a calibration data-cube obtained with a comparison lamp
  and a narrow-band filter to map how this shift have to applied. We call this 
  map the _phase-map_. This script measures that by using `numpy.argmax`. 
  
  This script also measures:
  
  * The _Free-Spectral-Range or FSR;
  * The center of the rings;
  * The _full-width at half-maximum_ (fwhm). 

  These three parameters are usefull for further steps in the data-reduction
  or even for data-acquisition. They are all stored in the header of the 
  phase-map extracted.
  
  
 
 ## phmfit.py
 
 ## apply.py
 
 ## wcal.py
