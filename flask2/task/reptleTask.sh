#!/bin/bash

# do reptile to get today data
`python /home/ly/Item/flask/reptile.py >> /home/ly/Item/flask/log/$(date +"%Y%m%d")_reptileLog.log`


