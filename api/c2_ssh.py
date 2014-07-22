import paramiko
import json

def conn(host,command,user="root",pwd=None,port=22):	
	ssh=paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(host,port,user,pwd)
	stdout,stderr=ssh.exec_command(command)
	ssh.close()
	error=stderr.readlines()
	if not error:
	    output=stdout.readlines()
	    ot_list=json.dumps(output)
	    print ot_list
	    return ot_list
	else:
	    errot_list=json.dumps(error)
	    print "An error happened by:%s" % errot_list
	    return None








