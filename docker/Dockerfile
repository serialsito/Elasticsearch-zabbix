FROM ubuntu:xenial

ENV DEBIAN_FRONTEND noninteractive

RUN  apt-get update \
  && apt-get install -y wget
RUN wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add
RUN apt-get update
RUN apt-get install -y software-properties-common
RUN add-apt-repository 'deb http://packages.elastic.co/elasticsearch/2.x/debian stable main'
RUN apt-get install -y git
RUN apt-get install -y python-pip

RUN apt-get update && apt-get install -y supervisor
RUN mkdir -p /var/log/supervisor
ADD ./config/elasticsearch.conf /etc/supervisor/conf.d/elasticsearch.conf
ADD ./config/zabbix-agent.conf /etc/supervisor/conf.d/zabbix-agent.conf
CMD ["/usr/bin/supervisord"]


RUN wget http://repo.zabbix.com/zabbix/3.2/ubuntu/pool/main/z/zabbix/zabbix-agent_3.2.0-1+xenial_amd64.deb
RUN apt-get install libcurl3 && dpkg -i zabbix-agent_3.2.0-1+xenial_amd64.deb
ADD ./ /opt/elasticsearch-zabbix/
ADD ./config/zabbix_agentd.conf /etc/zabbix/zabbix_agentd.conf
RUN cd /opt/ \
  &&  ls -la /opt/elasticsearch-zabbix/ \
  &&  cp -fv /opt/elasticsearch-zabbix/ESzabbix.userparm /etc/zabbix/zabbix_agentd.d/elasticsearch.conf \
  &&  sed -i 's/\/opt\/zabbix\/externalscripts/\/opt\/elasticsearch-zabbix/g' /etc/zabbix/zabbix_agentd.d/elasticsearch.conf \
  &&  chown -v -R zabbix:zabbix /opt/elasticsearch-zabbix \
  &&  pip install pyes elasticsearch
    # check all working
USER zabbix
RUN /opt/elasticsearch-zabbix/ESzabbix.py service status \
  && /opt/elasticsearch-zabbix/ESzabbix.py cluster status
