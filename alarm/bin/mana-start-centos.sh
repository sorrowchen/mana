#!/bin/sh
#. /etc/rc.d/init.d/functions

#daemon  --user cinder --pidfile $pidfile "$exec --config-file $distconfig --config-file $config --logfile $logfile &>/dev/null & echo \$! > $pidfile"
#daemon  --pidfile /tmp/mana_monitor.pid -- "/opt/projects/mana/alarm/mana_monitor.py &> /dev/null "                                  
nohup /opt/projects/mana/alarm/mana_monitor.py > /dev/null 2>&1 &
