#!/usr/bin/python
#coding:utf-8
import paramiko
import json
import os
from StringIO import StringIO

PUBLIC_KEY="""
ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAvRW4Zsw2fsNUEmHR/d3yaLC+5aqcDVrXZwtbGKr5jQalhuwdrezJxu7INXtuVa24o0S+0AxjXd9rdmKBAkR7e0OUgiAGm4HQEssA5iymKvqCcl+zVDUcytHSU87fG6JGuk5IJSdhxyvc2LclS5QZjvwZl/6DkrVQ/fslv1ekwYug6hbPoF8Ovvdi7dGvFZhw6i4alxvGuu3Mq1XsPZGG/fbQyK8gTsDZ6VjIoqZRP1D0TbXebz7S7CK1cYHJufKN6Q0WZALBIQI1u/XWoZdsRSqt/TAhkOUOg7S0jM8SSRO2JfRJbcx+iLbruFLj7kzgscBaWTgcG9lMyg3f5e8/qw== root@ypt_server10
"""

def conn(host,command,user="root",pwd=None,port=22):	
	ssh=paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	print "host:%s,command:%s,user:%s,pwd:%s,port:%s" % (host,command,user,pwd,port)
        key = paramiko.RSAKey.from_private_key(StringIO(PUBLIC_KEY), password=passphrase)
	ssh.connect(host,port,user,pwd,pkey=key)
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





