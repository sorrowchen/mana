#!/usr/bin/python
#coding:utf-8
import paramiko
import json
import os

def conn(host,command,user="root",pwd=None,port=22):	
	ssh=paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	print "host:%s,command:%s,user:%s,pwd:%s,port:%s" % (host,command,user,pwd,port)
	PRIVATE_KEY='/root/.ssh/id_rsa'
        #key = paramiko.RSAKey.from_private_key(PRIVATE_KEY,password=None)
	#ssh.load_system_host_keys()
	ssh.connect(host,port,user,pwd,key_filename=PRIVATE_KEY)
	print "------start read----"
	stdin,stdout,stderr=ssh.exec_command(command)
	print "------read end-------"
	print type(stderr)
	error=stderr.readlines()
	print type(error)
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





