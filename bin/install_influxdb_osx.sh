#!/bin/sh


location=$1


brew update 2>&1 >> install_log;

brew install influxdb 2>&1 >> install_log;
mkdir "$1" 
path="$(find /usr/local/Cellar -type f -name "influxd")"



ln -s $path $location 2>&1 >> install_log;

exit;



