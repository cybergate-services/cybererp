#!/bin/bash

chown --recursive asterisk:asterisk /var/lib/asterisk
chown --recursive asterisk:asterisk /var/log/asterisk
chown --recursive asterisk:asterisk /var/run/asterisk
chown --recursive asterisk:asterisk /var/spool/asterisk
chown --recursive asterisk:asterisk /usr/lib/asterisk
chown --recursive asterisk:asterisk /dev/zap
#----------------------------------------------------
chmod --recursive u=rwX,g=rX,o= /var/lib/asterisk
chmod --recursive u=rwX,g=rX,o= /var/log/asterisk
chmod --recursive u=rwX,g=rX,o= /var/run/asterisk
chmod --recursive u=rwX,g=rX,o= /var/spool/asterisk
chmod --recursive u=rwX,g=rX,o= /usr/lib/asterisk
chmod --recursive u=rwX,g=rX,o= /dev/zap
#----------------------------------------------------
chown --recursive root:asterisk /etc/asterisk
chmod --recursive u=rwX,g=rX,o= /etc/asterisk
#----------------------------------------------------
# Asterisk needs to write to voicemail.conf for password change.
chmod g+w /etc/asterisk/voicemail.conf
chmod g+w,+t /etc/asterisk
#----------------------------------------------------
