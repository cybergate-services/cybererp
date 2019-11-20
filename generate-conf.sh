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

echo "Enter SMTP host that will be used to send mails from Odoo"
while [ -z "${SMTP_HOST}" ]; do
  read -p "SMTP Host: " -e SMTP_HOST
  DOTS=${SMTP_HOST//[^.]};
  if [ ${#DOTS} -lt 2 ] && [ ! -z ${SMTP_HOST} ]; then
    echo "${SMTP_HOST} is not a FQDN"
    CYBERERP_HOSTNAME=
  fi
done

echo "Enter mail account to be used as Odoo and pgAdmin Administrator account"
while [ -z "${ODOO_EMAIL}" ]; do
  read -p "Admintrator's Email: " -e ODOO_EMAIL
  ATS=${ODOO_EMAIL//[^@]};
  if [ ${#ATS} -ne 1 ] && [ ! -z ${ODOO_EMAIL} ]; then
    echo "${ODOO_EMAIL} is not a valid email"
    ODOO_EMAIL=
  fi
done

echo "Enter SMTP user that will be used to send mails from Odoo"
while [ -z "${SMTP_USER}" ]; do
  read -p "SMTP User: " -e SMTP_USER
  ATS=${SMTP_USER//[^@]};
  if [ ${#ATS} -ne 1 ] && [ ! -z ${SMTP_USER} ]; then
    echo "${SMTP_USER} is not a valid email address"
    SMTP_USER=
  fi
done

echo "Enter SMTP User Password that will be used to send mails from Odoo"
while [ -z "${SMTP_PASSWORD}" ]; do
  read -p "SMTP Password: " -e SMTP_PASSWORD
  count=`echo ${#SMTP_PASSWORD}`
  # echo $count
  if [[ $count -lt 8 ]];then
     echo "Password length should be at least 8 charactors"
     SMTP_PASSWORD=
  fi
  echo ${SMTP_PASSWORD} | grep "[A-Z]" | grep "[a-z]" | grep "[0-9]" | grep "[@#$%^&*]"
  if [[ $? -ne 0 ]];then
    echo "Password must contain upparcase ,lowecase,number and special charactor"
    SMTP_PASSWORD=
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

PASSWORD=$(LC_ALL=C </dev/urandom tr -dc A-Za-z0-9 | head -c 28)

HTPASSWD=$(which htpasswd) 
if [ -z "${HTPASSWD}" ]; then
  echo "htpasswd command is not found and installing it now..."
  sudo apt install -y apache2-utils
  htpasswd -b -c ./conf/htpasswd admin ${PASSWORD}
else 
  htpasswd -b -c ./conf/htpasswd admin ${PASSWORD}
fi

POSTGRESQL_PASSWORD=${PASSWORD}
ODOO_PASSWORD=${PASSWORD}
ADMIN_PASSWORD=${PASSWORD}
PUID=1002
PGID=1002
URL=$(echo ${CYBERERP_HOSTNAME} | cut -n -f 1  -d . --complement)
SUBDOMAINS=odoo,odoo-pgadmin,odoo-portainer,odoo-backup
EXTRA_DOMAINS=
VALIDATION=http
EMAIL=${ODOO_EMAIL}
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
POSTGRESQL_PASSWORD=${PASSWORD}

# --------------------
# PGADMIN Environment
# --------------------
PGADMIN_PASSWORD=${PASSWORD}
PGADMIN_EMAIL=${EMAIL}

# -------------------
# ODOO Environment
# -------------------
ODOO_EMAIL=${ODOO_EMAIL}
ODOO_PASSWORD=${ODOO_PASSWORD}
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=${PASSWORD}
POSTGRESQL_HOST=postgresql
POSTGRESQL_PORT_NUMBER=5432
SMTP_HOST=${SMTP_HOST}
SMTP_PORT=465
SMTP_USER=${SMTP_USER}
SMTP_PASSWORD=${SMTP_PASSWORD}
SMTP_PROTOCOL=ssl
#-------------------------
# LETSENCRYPT Environment
#-------------------------
PUID=${PUID}
PGID=${PGID}
URL=${URL}
SUBDOMAINS=${SUBDOMAINS}
EXTRA_DOMAINS=${EXTRA_DOMAINS}
VALIDATION=${VALIDATION}
EMAIL=${EMAIL}
DHLEVEL=${DHLEVEL}
ONLY_SUBDOMAINS=${ONLY_SUBDOMAINS}
STAGING=${STAGING}
TZ=${CYBERERP_TZ}
EOF

ln ./cybererp.conf ./.env
mkdir -p ./postgresql_data
chmod 1777 ./postgresql_data
