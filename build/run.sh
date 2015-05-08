#!/bin/sh
cd /opt/projects/mana
uwsgi -x django_socket.xml
