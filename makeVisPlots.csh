#!/bin/tcsh

# Trigger creation of scheduler plots, if required
# Lives in /usr/local/cron/scripts/
# Executed by cron job:
# */10 * * * * /usr/local/cron/scripts/makeVisPlots.csh >& /dev/null

set job_dir = /ngts/staging/archive/jobs/vis_plots/
cd $job_dir

foreach job ( run_????-??-?? )
  set night = `echo $job | cut -d'_' -f 2`
  ssh -f dra@ngts-wrk-head.local "/usr/local/cron/scripts/schedule_visualiser.py $night"
  \rm $job
end

cd -
