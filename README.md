#SAM-FP

 This page contains some scripts that help me (and hopefully will
 help you too) to reduce Fabry-Perot data obtained at 
 [SOAR Telescope](http://www.ctio.noao.edu/soar/) with 
 [SOAR Adaptive Module](http://www.ctio.noao.edu/soar/content/soar-adaptive-optics-module-sam),
 or SAM. 

 This observing mode is considered a Restricted User Instrument and you 
 will have support to reduce, edit, visualize and manipulate your data.

 Scripts for data-reduction are saved inside the `scripts` folder. Each script 
 is described individually in our Wiki page. 
 
# How to Install

 We wrote `samfp` in Python 2 but, in principle, it should be compatible with 
 Python 3. We simply did not have the chance yet to actually test the Py2 to Py3
 conversion.

 Since there are several ways which one can install a Python library, we decided
 to develop `samfp` using the [Astroconda](https://astroconda.readthedocs.io/en/latest/)
 under [Anaconda](https://www.continuum.io/downloads). Once you have both installed
  and running properly, activate the Astroconda Virtual Environment by typing
  
  ```bash
   source activate astroconda
  ```
  in a terminal.
  
  After that, use `pip` to install `samfp` and its requirements:
  
  ```bash
  cd $path_to_samfp
  pip install -r requirements.txt
  pip install . 
  ```
  There is a know problem where both Numpy and SciPy fails to run under
  Anaconda because of a library called `mkl`. To fix that, type the following 
  command
  
  ```bash
  conda install nomkl
  ```
  
    