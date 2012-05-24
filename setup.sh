#!/bin/bash

#for some reason some packages will only install while inside the home directory...
cd ~

# install setuptools, so we can use easy_install for installing python packages
sudo apt-get install python-setuptools

sudo apt-get install build-essential python-dev

# install tweepy, a python library for the Twitter API
sudo easy_install tweepy

# install flickrapi, a python library for the Flickr API
sudo easy_install flickrapi

#install mongodb (on Ubuntu)
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10
if [ `grep -cE '^deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen$' /etc/apt/sources.list` = "0" ]; then
    sudo sh -c "echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' >> /etc/apt/sources.list"
fi
sudo apt-get update
sudo apt-get install mongodb-10gen

#install pymongo, a python library for mongodb
sudo easy_install pymongo

#install foursquare, a python library for the FourSquare API
sudo easy_install foursquare

#install instagram, a python library for the Instagram API
sudo easy_install python_instagram
