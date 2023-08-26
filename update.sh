#!/bin/bash

service_filename="rzd-tickets.service"

echo "Updating Project ($service_filename) with GitHub. Project directory - `pwd`"
git pull origin master
systemctl restart $service_filename