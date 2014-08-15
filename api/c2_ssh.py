#!/usr/bin/python
#coding:utf-8
import paramiko
import json
import os
from StringIO import StringIO

PUBLIC_KEY='/root/.ssh/id_rsa'

def conn(host,command,user="root",port=22):	
	ssh=paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	print "host:%s,command:%s,user:%s,pwd:%s,port:%s" % (host,command,user,pwd,port)
        key = paramiko.RSAKey.from_private_key(StringIO(PUBLIC_KEY))
	ssh.load_system_host_keys()
	ssh.connect(host,port,user,pkey=key)
	stdin,stdout,stderr=ssh.exec_command(command)
	error=stderr.readlines()
	output=stdout.readlines()
	ssh.close()
	if not error:
	    ot_list=json.dumps(output)
	    print ot_list
	    return ot_list
	else:
	    errot_list=json.dumps(error)
	    print "An error happened by:%s" % errot_list
	    return "An _error_ happened by:%s" % errot_list


def sudo_conn(host,cmd):
    stream=os.popen("sudo python sudo_ssh.py '%s' %s" % (host,cmd)).read()
    return stream





