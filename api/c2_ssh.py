#!/usr/bin/python
#coding:utf-8
import paramiko
import json

def conn(host,command,user="root",pwd=None,port=22):	
	ssh=paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	print "host:%s,command:%s,user:%s,pwd:%s,port:%s" % (host,command,user,pwd,port)
	ssh.connect(host,port,user,pwd)
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
	    return None








