===============================================
 Asterisk Base Application documentation
===============================================

**DOCUMENTATION IS UNDER CONSTRUCTION**

.. contents::
   :depth: 4


Installation videos
-------------------

* `How to connect your existing server`_

.. _How to connect your existing server: http://youtu.be/djLifLYITmE

Installation manual
-------------------

Docker based installation
#########################

In a module package asterisk_base there is a *deploy* folder where Docker compose style installation is available.

This is the prefered way of installing the **complete PBX**.

You get Odoo with Asterisk connected to it. 

Do not edit docker-compose.yml. Instead create docker-compose.overide.yml and put there
your local environment values. 

See docker-compose.override.yml.dev.example and docker-compose.override.yml.production.example
for references.

Start the project:

.. code::

 docker-compose up -d

During the installation procedure new postgresql database *asterisk_base* is created and 
asterisk_base addon is automatically installed.

During the installation process Asterisk Agent cannot 
connect to Odoo (as it's not ready yet) and gives Odoo connect errors but you can safely ignore them
as Agent will connect to Odoo when *asterisk_base* addon is completely setup.


The difference of production deploy from development:

- All communications are proxied by Nginx
- PostgreSQL port 5432 is not mapped
- Odoo ports 8069 & 8072 are not mapped so Odoo is available only from Nginx.
- Asterisk network_mode=host
- Nginx / location is password protected, default password is pbx / open (please change it in nginx/passwd)
- Asterisk console port 8010 is not mapped is also available only from Nginx.
- Remote Asterisk Agent connects though Nginx on port 44444 where only json-rpc is allowed.

Nginx notes
+++++++++++
Please note when nginx image is used it is http auth enabled.

**Default HTTP AUTH password is pbx / open.** You can leave it as is because Odoo authentication
is still active. Nginx http auth just protects you from automatic scanners.

Connecting existing server
##########################
In this case you have Odoo installation separated from your (existing) Asterisk server.
You can install Odoo as you wish either from the above docker examples or anyhow.
Asterisk base application must already be installed.

Now you need to install Agent script to your Asterisk server.

Docker based Agent installation
+++++++++++++++++++++++++++++++
You can download the Agent image from the Hub:

.. code::

 agent:
   image: odooist/asterisk_base_agent:latest
   restart: unless-stopped
   volumes:
     - /etc/asterisk/:/etc/asterisk/
     - /var/spool/asterisk/monitor:/var/spool/asterisk/monitor/
   environment:
     - DEBUG=0
     - ODOO_REGISTRATION_TOKEN=change-me
     - ODOO_DB=asterisk_base
     - ODOO_LOGIN=agent_test
     - ODOO_PASSWORD=agent_pass
     - ODOO_HOST=odoo
     - ODOO_PORT=8072
     - ODOO_SCHEME=http
     - ODOO_RECONNECT_INTERVAL=1
     - HOSTNAME=localhost
     - DOWNLOAD_CONF_AT_START=1
     - MANAGER_HOST=localhost
     - MANAGER_PORT=5038
     - MANAGER_LOGIN=odoo
     - MANAGER_PASSWORD=odoo
     - AMI_EVENT_AGENT_CALLED=0
     - TZ=Europe/Amsterdam
     - ASTERISK_CONF_DIR=/etc/asterisk
     - ASTERISK_SOUNDS_DIR=/var/lib/asterisk/sounds/
     - ASTERISK_BINARY=/usr/sbin/asterisk
     - MONITOR_DIR=/var/spool/asterisk/monitor
     - DELETE_RECORDING_FAILED_UPLOAD=1
     - REC_UPLOAD_DELAY=5
     - CONSOLE_LISTEN_ADDRESS=0.0.0.0
     - CONSOLE_LISTEN_PORT=8010
     - ORIGINATE_CONTEXT=odoo-outgoing
     - ORIGINATE_TIMEOUT=60



Manual installation
+++++++++++++++++++
From the *Asterisk->Settings->Base Settings* click *Download Agent installation package*.

Copy it to your asterisk server. Run:

.. code::

 tar xfz asterisk_base_agent.tar.gz
 cd asterisk_base_agent
 pip install -r requirements.txt

Review start.sh and correct environment variables if required. Start it:

.. code::

 ./start.sh
 2018-12-22 15:51:12,475 INFO Starting asterisk_base agent with UID s2482660048902
 2018-12-22 15:51:12,478 INFO Connecting to Asterisk.
 2018-12-22 15:51:12,479 INFO Registering to https://nginx:44444/asterisk_base/register_server with UID s2482660048902
 2018-12-22 15:51:12,514 INFO protocol version: '4.0.3'
 2018-12-22 15:51:12,518 INFO FullyBooted
 2018-12-22 15:51:12,771 INFO Register status: Server created
 2018-12-22 15:51:12,771 DEBUG Requesting all conf download
 2018-12-22 15:51:12,773 DEBUG Starting Odoo bus poll for asterisk_agent/s2482660048902
 2018-12-22 15:51:12,774 INFO Connecting to Odoo at https://nginx:44444
 2018-12-22 15:51:12,775 DEBUG Odoo authenticate
 ....



Architecture description
------------------------
Asterisk configuration from database **is not** used here (neither realtime nor static).

Instead, all Asterisk .conf files are stored in Odoo database and are delivered to Asterisk server
with special Asterisk agent script running on the same server.

All PBX entities are implemented as Odoo models. When a model is changed (new record created, updated or deleted)
it calls its *build_conf()* method to generate a special .conf file that is included from main .conf file.

The following .conf files are created:

* extensions_odoo.conf - here are extension numbers defined in Odoo *Extensions* menu.
* extensions_odoo_incoming.conf - *Routes -> Incoming* 
* extensions_odoo_outgoing.conf - *Routes -> Outgoing*
* extensions_odoo_custom.conf - *Dialplans* menu records come here.
* extensions_odoo_menu.conf - Odoo *Menus* come here.
* extensions_odoo_users.conf - User's individual call logic that comes from Users menu is here.
* sip_odoo_user.conf - SIP trunks of users with context set to *odoo-outgoing*.
* sip_odoo_trunk.conf - SIP trunks with context set to *odoo-incoming*
* voicemail_odoo.conf - if user defined a voicemail logic he will have a mailbox here.
* queues_odoo.conf - Odoo *Queues* come here.


Change Log
----------
1.0.1
#####
* Initial release.



Troubleshooting
---------------
Loosing executable flag
#######################
When your get this issue the following error message is displayed when you try to run the container:

.. code::

 ERROR: for asterisk_base_asterisk_1_fce11df9f715  Cannot start service asterisk: 
 OCI runtime create failed: container_linux.go:348: starting container process 
 caused "exec: \"/docker-entrypoint.sh\": permission denied": unknown

The problem is than on module unpack operation executable flags where lost. To fix it do the following:

.. code::

  chmod +x deploy/asterisk/*.sh
  chmod +x deploy/asterisk/services/*.py

Now rebuild the asterisk image.

OS X network_mode=host issue
############################
Mac has limitations with network in host mode.

So your only option is to map SIP and RTP ports.
Such a setup has limitations. Don't use it in production.


Additional information
----------------------
How to install Docker on Ubuntu 16.04
#####################################
Install Docker:

.. code::

 sudo apt-get update
 sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
 sudo apt-add-repository 'deb https://apt.dockerproject.org/repo ubuntu-xenial main'
 apt-get update
 sudo apt-get install -y docker-engine

Install Docker compose:

.. code::

 sudo curl -L https://github.com/docker/compose/releases/download/1.18.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
 sudo chmod +x /usr/local/bin/docker-compose



