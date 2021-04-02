#!/bin/bash

# exit on any error
set -e

# update raspbian
sudo apt-get update -q
sudo apt-get dist-upgrade -qy
sudo apt-get autoremove -qy
sudo apt-get autoclean -q
sudo ldconfig

# update pihole
pihole -up

# update pihole blocklists
sqlite3 /etc/pihole/gravity.db "SELECT Address FROM adlist" |sort >/home/pi/pihole.list
wget -qO - https://raw.githubusercontent.com/hemiipatu/PiHoleBlocklists/master/lists.txt |sort >/home/pi/piholeblocklists.list
comm -23 pihole.list piholeblocklists.list |xargs -I{} sudo sqlite3 /etc/pihole/gravity.db "DELETE FROM adlist WHERE Address='{}';"
comm -13 pihole.list piholeblocklists.list |xargs -I{} sudo sqlite3 /etc/pihole/gravity.db "INSERT INTO adlist (Address,Comment,Enabled) VALUES ('{}','piholeblocklists, added `date +%F`',1);"
pihole restartdns reload-lists
pihole -g