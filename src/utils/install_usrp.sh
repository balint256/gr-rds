#!/bin/bash

sudo addgroup usrp
sudo addgroup `whoami` usrp
echo ACTION==\"add\",\ BUS==\"usb\",\ SYSFS{idVendor}==\"fffe\",\ SYSFS{idProduct}==\"0002\",\ GROUP:=\"usrp\",\ MODE:=\"0660\" > tmpfile
sudo chown root.root tmpfile
sudo mv tmpfile /etc/udev/rules.d/10-usrp.rules
echo /usr/local/lib | sudo tee -a /etc/ld.so.conf
sudo ldconfig

sudo chmod u+s /usr/local/bin/usrp2_socket_opener
[ -a /etc/security/limits.d ] || sudo mkdir /etc/security/limits.d
echo '@usrp  - rtprio 50' | sudo tee /etc/security/limits.d/usrp.conf
