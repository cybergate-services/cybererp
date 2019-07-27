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

cat << EOF > openemail.conf
# --------------------------------------
# CyberERP docker-compose configuration
# --------------------------------------
CYBERERP_HOSTNAME=${OPENEMAIL_HOSTNAME}

# ----------------------------------
# POSTGRESQL database configuration
# ----------------------------------
POSTGRES_DB=${POSTGRES_DB}
POSTGRES_USER=${POSTGRES_USER}
PGDATA=${PGDATA}

# -------------------
# ODOO Configuration
# -------------------
ODOO_PASSWORD=${ODOO_PASSWORD}
ADDONS_PATH=${ADDONS_PATH}

# You should use HTTPS, but in case of SSL offloaded reverse proxies:

HTTP_PORT=80
HTTP_BIND=0.0.0.0

HTTPS_PORT=443
HTTPS_BIND=0.0.0.0

# ------------------------------
# Other bindings
# ------------------------------
# You should leave that alone
# Format: 11.22.33.44:25 or 0.0.0.0:465 etc.
# Do _not_ use IP:PORT in HTTP(S)_BIND or HTTP(S)_PORT

SMTP_PORT=25
SMTPS_PORT=465
SUBMISSION_PORT=587
IMAP_PORT=143
IMAPS_PORT=993
POP_PORT=110
POPS_PORT=995
SIEVE_PORT=4190
DOVEADM_PORT=127.0.0.1:19991
SQL_PORT=127.0.0.1:13306

# Your timezone

TZ=${OPENEMAIL_TZ}

# Fixed project name

COMPOSE_PROJECT_NAME=openemail

# Set this to "allow" to enable the anyone pseudo user. Disabled by default.
# When enabled, ACL can be created, that apply to "All authenticated users"
# This should probably only be activated on mail hosts, that are used exclusivly by one organisation.
# Otherwise a user might share data with too many other users.
ACL_ANYONE=disallow

# Garbage collector cleanup
# Deleted domains and mailboxes are moved to /var/vmail/_garbage/timestamp_sanitizedstring
# How long should objects remain in the garbage until they are being deleted? (value in minutes)
# Check interval is hourly

MAILDIR_GC_TIME=1440

# Additional SAN for the certificate
#
# You can use wildcard records to create specific names for every domain you add to openemail.
# Example: Add domains "example.com" and "example.net" to openemail, change ADDITIONAL_SAN to a value like:
#ADDITIONAL_SAN=imap.*,smtp.*
# This will expand the certificate to "imap.example.com", "smtp.example.com", "imap.example.net", "imap.example.net"
# plus every domain you add in the future.
#
# You can also just add static names...
#ADDITIONAL_SAN=srv1.example.net
# ...or combine wildcard and static names:
#ADDITIONAL_SAN=imap.*,srv1.example.com
#

ADDITIONAL_SAN=

# Skip running ACME (acme-openemail, Let's Encrypt certs) - y/n

SKIP_LETS_ENCRYPT=n

# Skip IPv4 check in ACME container - y/n

SKIP_IP_CHECK=n

# Skip ClamAV (clamd-openemail) anti-virus (Rspamd will auto-detect a missing ClamAV container) - y/n

SKIP_CLAMD=${SKIP_CLAMD}

# Skip Solr on low-memory systems or if you do not want to store a readable index of your mails in solr-vol-1.
SKIP_SOLR=${SKIP_SOLR}

# Solr heap size in MB, there is no recommendation, please see Solr docs.
# Solr is a prone to run OOM and should be monitored. Unmonitored Solr setups are not recommended.
SOLR_HEAP=1024

# Enable watchdog (watchdog-openemail) to restart unhealthy containers (experimental)

USE_WATCHDOG=n

# Send notifications by mail (no DKIM signature, sent from watchdog@OPENEMAIL_HOSTNAME)
# Can by multiple rcpts, NO quotation marks

#WATCHDOG_NOTIFY_EMAIL=a@example.com,b@example.com,c@example.com
#WATCHDOG_NOTIFY_EMAIL=

# Max log lines per service to keep in Redis logs

LOG_LINES=9999

# Internal IPv4 /24 subnet, format n.n.n (expands to n.n.n.0/24)

IPV4_NETWORK=172.22.1

# Internal IPv6 subnet in fc00::/7

IPV6_NETWORK=fd4d:6169:6c63:6f77::/64

# Use this IPv4 for outgoing connections (SNAT)

#SNAT_TO_SOURCE=

# Use this IPv6 for outgoing connections (SNAT)

#SNAT6_TO_SOURCE=

# Create or override API key for web uI
# You _must_ define API_ALLOW_FROM, which is a comma separated list of IPs
# API_KEY allowed chars: a-z, A-Z, 0-9, -

#API_KEY=
#API_ALLOW_FROM=127.0.0.1,1.2.3.4

EOF

mkdir -p data/assets/ssl

# copy but don't overwrite existing certificate
cp -n data/assets/ssl-example/*.pem data/assets/ssl/

ln /opt/openemail/openemail.conf /opt/openemail/.env
