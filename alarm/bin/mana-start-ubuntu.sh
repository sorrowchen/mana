start-stop-daemon --start --startas /usr/bin/python "/home/ywy/sourcecode/mana/alarm/mana_monitor.py" --pidfile /var/run/mana/mana_monitor.pid  --background > /dev/null 
#start-stop-daemon --start --background /usr/bin/python /home/ywy/sourcecode/mana/alarm/mana_monitor.py  > /dev/null 

