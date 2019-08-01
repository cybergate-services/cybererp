# CyberERP: Containerized Odoo

![](images/odoo-intro.jpg)
Odoo is the most popular all-in-one business software in the world. It offers a range of business applications including CRM, website, e-Commerce, billing, accounting, manufacturing, warehouse, project management, inventory and much more, all are seamlessly integrated.

CyberERP is an effort to deploy an enterprise ready  containerized  Open Source Odoo ERP system with several other required and optional containers. This system can be extended to provide highly available Odoo ERP system and it  contains Open Source Odoo ERP software together with several other community provided addon modules. 

You have been relieved from complexity of installing Odoo manually and connecting with a postgresql database which is running in a different container.  In addition to these we have also integrated several other complex applications which are running in containers.  You will only take a few minutes to deploy an extremely complex system thanks to Docker technologies which would otherwise taken to deploy several days. 

Our solution  consists of the following containers and you  visit the following links to understand what role each container will play in our Odoo deployment. 

1. [linuxserver/letsencrypt](https://hub.docker.com/r/linuxserver/letsencrypt)
2. [linuxserver/heimdall](https://hub.docker.com/r/linuxserver/heimdall)
3. [odoo](https://hub.docker.com/_/odoo)
4. [postgres](https://hub.docker.com/_/postgres)
5. [dpage/pgadmin4](https://hub.docker.com/r/dpage/pgadmin4)
6. [google/cadvisor](https://hub.docker.com/r/google/cadvisor)
7. [prom/prometheus](https://hub.docker.com/r/prom/prometheus)
8. [redis](https://hub.docker.com/_/redis)
9. [portainer/portainer](https://hub.docker.com/r/portainer/portainer)
10. [tiredofit/db-backup](https://hub.docker.com/r/tiredofit/db-backup)
11. [linuxserver/duplicati](https://hub.docker.com/r/linuxserver/duplicati)

# Deployment

This guide assuemes that you have already install your docker daemon and docker-compose tools in your docker host. We have tested this solution both on Debian 9(Stretch) and Ubuntu 18.04 LTS (Bionic). If you haven't prepare your Docker host yet, you may use the following links to get your task done.

## Preparing Debian/Ubuntu Systems as Docker Hosts

* [To Install Docker CE in Ubuntu](https://docs.docker.com/v17.09/engine/installation/linux/docker-ce/ubuntu/)
* [To Install Docker CE on Debian](https://docs.docker.com/v17.09/engine/installation/linux/docker-ce/debian/)
* [To Install Compose on Linux systems](https://docs.docker.com/compose/install/)

NOTE: Installing docker-compose in Linux is same any distribution of Linux.

Install the following addtional tools
```bash
sudo apt install git apache2-utils
```
# Adding DNS Entries

Our setup requires DNS A records for all of our applications which are running in containers and accessing their interfaces over HTTPS. Letsencrypt container requires DNS A records to be created and available for all the subdomains for the following application interfaces. The example domain which we are using in this guide is ```cybergatelabs.com```.

Create A records for all the subdomains which are listed in the table below. Please ask your DNS administrator to create those records if you do not have administrative access for your corporate DNS servers. 

Container | subdoamin | Web Interface
----------|-----------|---------------
heimdal | bis.cybergatelabs.com | Application dash board
odoo | odoo.cybergatelabs.com | Odoo Web UI
padamin | pagadmin.cybergatelabs.com | pgAdmin Web UI
cadvisor | cadvisor.cybergatelabs.com | cAdvisor Web UI for container performance monitoring 
prometheus | prometheus.cybergatelabs.com | Prometheus Web UI for container performance monitoring 
portainer | portainer.cybergatelabs.com | Portainer Web UI for container mangement

# Deploying CyberERP

In this section we have given you instruction to setup. Execute the following commands in the same order as I have listed. 

1. Login to your docker host and become ```root``` and change your direcory to ```/opt```
   ```bash
   sudo su -
   cd /opt
   ```
2. Clone the ```CyberERP``` repository.
   ```bash
   git clone https://github.com/cybergate-services/cybererp.git
   ```
3. Create the storage directory

   This directory is used to host the persistent data volumes of our containers. It also used to host the data backup from      containers. This guide uses ```/opt/backup```  directory for this purpose. You may mount a volume from your enterprise SAN    or NAS which will provide more robust and resilient storage environment  for your Odoo deployment.
   ```bash
   mkdir /opt/storage
   ```
 4. Generate enviorenemnet variables
   
    We wiil need this step to create ```cybererp.conf``` which will contain neccessary enviorenment variables that are 
    required by the ```docker-compose.yml``` file.
    ```bash
    cd /opt/cybererp
    ./generate-conf.sh 
    ```
    Below is a sample output from an above operation.
    
    ```bash
    Press enter to confirm the detected value '[value]' where applicable or enter a custom value.
    Hostname (FQDN): bis.cybergate.lk
    Enter mail account to be used as Odoo and pgAdmin Administrator account
    Admintrator's Email: bisadmin@cybergate.lk
    Timezone: Asia/Colombo
    Adding password for user admin
    
 5. Deploy and start the containers.
 
    ```bash
    docker-compose up -d
    ```
 6. Check the running status of the containers
 
    ```bash
    docker-compose ps
    ```
    You will get an output like below.   
    ```
       Name                  Command               State                    Ports                  
    -----------------------------------------------------------------------------------------------
    cadvisor      /usr/bin/cadvisor -logtostderr   Up      0.0.0.0:8080->8080/tcp                  
    db-backup     /init                            Up      10050/tcp, 1025/tcp, 8025/tcp           
    duplicati     /init                            Up      0.0.0.0:8200->8200/tcp                  
    heimdall      /init                            Up      443/tcp, 80/tcp                         
    letsencrypt   /init                            Up      0.0.0.0:443->443/tcp, 0.0.0.0:80->80/tcp
    odoo          /entrypoint.sh odoo              Up      8069/tcp, 8071/tcp                      
    pgadmin       /entrypoint.sh                   Up      443/tcp, 80/tcp                         
    portainer     /portainer                       Up      9000/tcp                                
    postgresql    docker-entrypoint.sh postgres    Up      5432/tcp                                
    prometheus    /bin/prometheus --config.f ...   Up      0.0.0.0:9090->9090/tcp                  
    redis         docker-entrypoint.sh redis ...   Up      0.0.0.0:6379->6379/tcp
    ```
    # Intial Odoo Configuration
    
    In this section we will cary out the intial confiuration of our odoo conatiner. 
    
    
    
    
