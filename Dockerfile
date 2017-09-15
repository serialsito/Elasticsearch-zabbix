FROM ubuntu:xenial

ENV DEBIAN_FRONTEND noninteractive

RUN  apt-get update \
  && apt-get install -y wget

RUN apt-get update
RUN apt-get install -y software-properties-common

RUN wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add
RUN add-apt-repository 'deb http://packages.elastic.co/elasticsearch/2.x/debian stable main'
RUN apt-get update
RUN apt-get install elasticsearch=2.1.1

RUN add-apt-repository -y ppa:webupd8team/java
RUN echo debconf shared/accepted-oracle-license-v1-1 select true |  debconf-set-selections
RUN echo debconf shared/accepted-oracle-license-v1-1 seen true | debconf-set-selections
RUN apt-get update
RUN wget http://download.oracle.com/otn-pub/java/jdk/8u144-b01/090f390dda5b47b9b721c7dfaa008135/jdk-8u144-linux-i586.tar.gz
RUN mkdir -p /var/cache/oracle-jdk8-installer
RUN mv jdk-8u144-linux-i586.tar.gz /var/cache/oracle-jdk8-installer/jdk-8u144-linux-i586.tar.gz
RUN apt-get install -y oracle-java8-installer
RUN java -version

RUN apt-get install -y git
RUN apt-get install -y python-pip

RUN wget -qO - http://repo.zabbix.com/zabbix-official-repo.key | apt-key add
RUN apt-add-repository "deb http://repo.zabbix.com/zabbix/3.2/ubuntu/ xenial main"
RUN apt-get update
RUN apt-get install -y zabbix-agent


ADD ./ /opt/elasticsearch-zabbix/
RUN cd /opt/ \
  &&  ls -la /opt/elasticsearch-zabbix/ \
  &&  cp -fv /opt/elasticsearch-zabbix/ESzabbix.userparm /etc/zabbix/zabbix_agentd.d/elasticsearch.conf \
  &&  sed -i 's/\/opt\/zabbix\/externalscripts/\/opt\/elasticsearch-zabbix/g' /etc/zabbix/zabbix_agentd.d/elasticsearch.conf \
  &&  chown -v -R zabbix:zabbix /opt/elasticsearch-zabbix \
  &&  pip install pyes elasticsearch

RUN apt-get install -y supervisor
RUN mkdir -p -m 0777 /var/log/supervisor
RUN mkdir -p -m 0777 /var/run/zabbix

ADD ./docker/config/zabbix/zabbix_agentd.conf /etc/zabbix/zabbix_agentd.conf
ADD ./docker/config/supervisor/elasticsearch.conf /etc/supervisor/conf.d/elasticsearch.conf
ADD ./docker/config/supervisor/zabbix-agent.conf /etc/supervisor/conf.d/zabbix-agent.conf
CMD ["supervisord", "-n","-c", "/etc/supervisor/supervisord.conf"]