#!/usr/bin/env bash

if [ -f cybererp.conf ]; then
  read -r -p "A config file exists and will be overwritten, are you sure you want to contine? [y/N] " response
  case $response in
    [yY][eE][sS]|[yY])
      mv cybererp.conf cybererp.conf_backup
      ;;
    *)
      exit 1
    ;;
  esac
fi

if [ -f ./.env ]; then
 rm -f 
 ./.env
fi

echo "Press enter to confirm the detected value '[value]' where applicable or enter a custom value."
while [ -z "${CYBERERP_HOSTNAME}" ]; do
  read -p "Hostname (FQDN): " -e CYBERERP_HOSTNAME
  DOTS=${CYBERERP_HOSTNAME//[^.]};
  if [ ${#DOTS} -lt 2 ] && [ ! -z ${CYBERERP_HOSTNAME} ]; then
    echo "${CYBERERP_HOSTNAME} is not a FQDN"
    CYBERERP_HOSTNAME=
  fi
done

if [ -a /etc/timezone ]; then
  DETECTED_TZ=$(cat /etc/timezone)
elif [ -a /etc/localtime ]; then
  DETECTED_TZ=$(readlink /etc/localtime|sed -n 's|^.*zoneinfo/||p')
fi

while [ -z "${CYBERERP_TZ}" ]; do
  if [ -z "${CYBERERP_TZ}" ]; then
    read -p "Timezone: " -e CYBERERP_TZ
  else
    read -p "Timezone [${DETECTED_TZ}]: " -e CYBERERP_TZ
    [ -z "${CYBERERP_TZ}" ] && CYBERERP_TZ=${DETECTED_TZ}
  fi
done

POSTGRES_DB=postgres 
POSTGRES_USER=odoo
PGDATA='/var/lib/postgresql/data/pgdata'
ADDONS_PATH='/mnt/extra-addons'
DATA_DIR='/var/lib/odoo'
POSTGRES_PASSWORD=$(LC_ALL=C </dev/urandom tr -dc A-Za-z0-9 | head -c 28)
ODOO_PASSWORD=$(LC_ALL=C </dev/urandom tr -dc A-Za-z0-9 | head -c 28)
ADMIN_PASSWORD=${ODOO_PASSWORD}
PUID=1002
PGID=1002
URL=cybergateservices.net
SUBDOMAINS=cybodo,
VALIDATION=http
EMAIL=erpadmin@cybergateservices.net 
DHLEVEL=2048 
ONLY_SUBDOMAINS=true 
STAGING=false

cat << EOF > cybererp.conf
# -------------------------------------
# CyberERP docker-compose Environment
# -------------------------------------
CYBERERP_HOSTNAME=${CYBERERP_HOSTNAME}

# ----------------------------------
# POSTGRESQL Database Environment
# ----------------------------------
POSTGRES_DB=${POSTGRES_DB}
POSTGRES_USER=${POSTGRES_USER}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
PGDATA=${PGDATA}

# -------------------
# ODOO Environment
# -------------------
ODOO_PASSWORD=${ODOO_PASSWORD}
ADDONS_PATH=${ADDONS_PATH}

#-------------------------
# LETSENCRYPT Environment
#-------------------------
PUID=${PUID}
PGID=${PGID}
URL=${URL}
SUBDOMAINS=${SUBDOMAINS}
VALIDATION=${VALIDATION}
EMAIL=${EMAIL}
DHLEVEL=${DHLEVEL}
ONLY_SUBDOMAINS=${ONLY_SUBDOMAINS}
STAGING=${STAGING}
TZ=${CYBERERP_TZ}
EOF

cat << EOF > ./conf/odoo/odoo.conf
# -------------------
# ODOO configuration
# -------------------
[options]
addons_path = ${ADDONS_PATH}
data_dir = ${DATA_DIR}
admin_passwd = ${ADMIN_PASSWORD}
db_name = ${POSTGRES_DB}
db_template = template1
dbfilter = .*
EOF

ln ./cybererp.conf ./.env
