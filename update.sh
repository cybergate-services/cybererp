#!/usr/bin/bash
#Get the updated images
docker pull bitnami/odoo:12

#Stop your odoo container
docker-compose stop odoo

#Take a snapshot of the application state
mkdir -p /opt/backup/odoo-bkp-$(date +%Y%m%d-%H.%M.%S)/
rsync -a /opt/cybererp/odoo_data/ /opt/backup/odoo-bkp-$(date +%Y%m%d-%H.%M.%S)/

#Get the updated image postgres
docker pull bitnami/postgresql:11

#Stop your postgres container
docker-compose stop postgresql

#Take a snapshot of the application state
mkdir -p /opt/backup/postgres-bkp-$(date +%Y%m%d-%H.%M.%S)/
rsync -a /opt/cybererp/postgresql_data/ /opt/backup/postgresql-bkp-$(date +%Y%m%d-%H.%M.%S)

#start the containers
docker-compose start postgresql ; docker-compose start odoo


