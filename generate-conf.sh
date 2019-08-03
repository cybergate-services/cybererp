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
  rm -f  ./.env
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

echo "Enter mail account to be used as Odoo and pgAdmin Administrator account"
while [ -z "${ADMIN_EMAIL}" ]; do
  read -p "Admintrator's Email: " -e ADMIN_EMAIL
  ATS=${ADMIN_EMAIL//[^@]};
  if [ ${#ATS} -ne 1 ] && [ ! -z ${ADMIN_EMAIL} ]; then
    echo "${ADMIN_EMAIL} is not a valid email"
    ADMIN_EMAIL=
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
PASSWORD=$(LC_ALL=C </dev/urandom tr -dc A-Za-z0-9 | head -c 28)

htpasswd -b -c ./conf/htpasswd admin ${PASSWORD}
PGADMIN_PASSWORD=$(LC_ALL=C </dev/urandom tr -dc A-Za-z0-9 | head -c 28)

ODOO_USER=odoo
POSTGRES_PASSWORD=${PASSWORD}
ODOO_PASSWORD=${PASSWORD}
ADMIN_PASSWORD=${PASSWORD}
PUID=1002
PGID=1002
URL=$(echo ${CYBERERP_HOSTNAME} | cut -n -f 1  -d . --complement)
SUBDOMAINS=bis,odoo,pgadmin,cadvisor,prometheus,portainer,duplicati
VALIDATION=http
EMAIL=${ADMIN_EMAIL}
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

# --------------------
# PGADMIN Environment
# --------------------
PGADMIN_PASSWORD=${PGADMIN_PASSWORD}
PGADMIN_EMAIL=${EMAIL}

# -------------------
# ODOO Environment
# -------------------
ODOO_PASSWORD=${ODOO_PASSWORD}
ODOO_DB=odoo
ODOO_USER=${ODOO_USER}
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
db_user = ${POSTGRES_USER}
db_template = template1
dbfilter = .*
EOF

ln ./cybererp.conf ./.env
