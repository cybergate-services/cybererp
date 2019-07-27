FROM odoo:12.0

USER root

RUN apt update && apt install -y git

RUN sed -i -- 's/; admin_passwd = admin/admin_passwd = you-must-change-me/g' /etc/odoo/odoo.conf

RUN pip3 install --no-binary :all: humanize

RUN mkdir -p /mnt/addons/tmp

RUN cd /mnt/addons/tmp && git clone -b 12.0 --depth=1 https://github.com/OCA/web && \
    mv web/web_notify /mnt/addons && rm -rf /mnt/addons/tmp

COPY ./ /mnt/addons/asterisk_base/
COPY ./deploy/odoo/odoo.conf /etc/odoo/odoo.conf

USER odoo

