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




