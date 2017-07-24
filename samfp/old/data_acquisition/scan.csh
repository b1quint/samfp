#!/bin/csh -f
# Setup
set basedir = "/home2/images/bquint/20161123/006"

sami dhe set image.type object
sami dhe set image.title "Ne_Lamp"
sami dhe set image.comment ""

set nsweeps = 1
set nchannels = 101
set nframes = 1
set fpzinit = 650
set stepsize = 4
set exptime = 1.0
set sleeptime = 0.0

if ("$1" != "") then
#use the argument as scan id
	set scid = $1
else
#otherwise just use the current date/time
	set dat = `date +%Y-%m-%dT%H:%M:%S`
	set scid = "SCAN_$dat"
endif
echo "SCAN $scid"

set basename_date = `date +"%Y%m%d_%H%M%S"`
echo $basename_date
set basename = "samfp$basename_date"

#these three keywords must correspond to matching keywords on the
#sami.hdr template to have this info added into the headers.
set sweepkey = "FAPERSWP"
set stepkey = "FAPERSST"
set scankey = "FAPERSID"

#sets the SAMI database variable $scankey as $scid. If this keyword is defined
#in the SAMI header template, this will appear on the header of the images
set cmd = `sami dhe dbs set $scankey $scid`
set cmd = `sami dhe dbs set "FPZINIT" $fpzinit`
set cmd = `sami dhe dbs set "FPZSTEP" $stepsize`
set cmd = `sami dhe dbs set "FPNCHAN" $nchannels`
echo "setting number of images, exposure time and basename"
sami dhe set obs.nimages $nframes
sami dhe set obs.exptime $exptime
sami dhe set image.dir $basedir
sami dhe set image.basename $basename
set scnt = 0
while ($nsweeps > $scnt)
	echo "moving FP to initial Z ($fpzinit)"
	sami fp moveabs $fpzinit
	set sweepid = "S"$scnt
#sets the SAMI database variable $sweepkey as $sweepid. If this keyword is defined
#in the SAMI header template, this will appear on the header of the images
	set cmd = `sami dhe dbs set $sweepkey $sweepid`
	echo "SWEEP $sweepid"
	set cnt = 0
	while ($nchannels > $cnt)
		if ($cnt > 0) then
			echo "moving FP by $stepsize"
			sami fp moveoff $stepsize
		endif
		set stepid = $sweepid"_"$cnt
#sets the SAMI database variable $stepkey as $stepid. If this keyword is defined
#in the SAMI header template, this will appear on the header of the images
		set cmd = `sami dhe dbs set $stepkey $stepid`
		echo "taking data...(sweep $sweepid step $cnt)"
        sleep $sleeptime
        sami dhe expose
		@ cnt = $cnt + 1
	end
	@ scnt = $scnt + 1
end

set scid = "---"
set cmd = `sami dhe dbs set $scankey $scid`
