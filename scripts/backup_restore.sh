#!/usr/bin/env bash
lbackuplocpost=/opt/cybererp/postgresql_data
lbackuplocodoo=/opt/cybererp/odoo_data

rbackuploc=/opt/backup/
DATE=`date +%Y%m%d%H%M`

#rsync -avp $lbackuplocpost :$rbackuploc
#rsync -avp $lbackuplocodoo :$rbackuploc

rsync -avp /opt/cybererp/postgresql_data /opt/backup/$DATE
rsync -avp /opt/cybererp/odoo_data /opt/backup/$DATE


find $rbackuploc/* -mtime +10 -exec rm {} \;
