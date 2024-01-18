#!/bin/bash

#get webServer Pid
pid=$(ps -ef|grep app.py |grep python | tr -s ' '|cut -d ' ' -f 2)

if [ "${pid}" ]
then
	kill ${pid}
fi
`python /home/ly/Item/flask/app.py`
